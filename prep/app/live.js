/* Prep Sarthi: Gemini Live as the interviewer, in the browser.
 *
 * A line-by-line port of the desktop app's gemini_realtime_live.py with the
 * roles flipped. Same BidiGenerateContent websocket, same setup message
 * (native-audio models only answer as speech, so audio is requested and both
 * transcriptions are switched on). Interrupted connections resume Google's
 * session when possible, or restore our transcript into a fresh session.
 *
 * What is different from the desktop engine:
 *   - the audio Gemini sends back is played (there it was discarded)
 *   - the microphone is the only input (there it was the meeting audio)
 *   - inputTranscription is what the CANDIDATE said, outputTranscription is
 *     what the INTERVIEWER said
 *   - `interrupted` clears the speaker queue (barge-in)
 *   - fresh sessions are nudged to speak first; resumed sessions continue
 *
 * Everything the page needs arrives through callbacks; nothing here touches
 * the DOM. Only the Gemini key the user pasted is ever sent, and only to
 * Google.
 */

import { NOTES } from "./interviewer.js?v=20260923-pacing";

// The desktop app's proven model first; the non-preview one if Google retires it.
export const LIVE_MODELS = ["gemini-3.1-flash-live-preview", "gemini-3.8-live"];
export const DEFAULT_MODEL = LIVE_MODELS[0];
const LIVE_URL = "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key=";
const CAPTURE_RATE = 16000;

const SETUP_TIMEOUT_SECONDS = 12;
const REPLY_TIMEOUT_SECONDS = 15;
const MAX_RETRIES = 5;
const MAX_BUFFERED_BYTES = 128000; // do not send seconds of stale microphone audio
const VOICE_RMS = 0.005;

const now = () => performance.now() / 1000;

export class Transcript {
  /* Ordered utterances: {who: "interviewer"|"candidate", text, start, end, interrupted}. */
  constructor() { this.items = []; this.open = { interviewer: null, candidate: null }; this.justClosed = null; }

  append(who, piece, t) {
    let u = this.open[who];
    if (!u) {
      // One person starts, the other's utterance is over; the engine emits it
      // as final right after this call (justClosed).
      const other = who === "interviewer" ? "candidate" : "interviewer";
      this.justClosed = this.close(other);
      u = { who, text: "", start: t, end: t, interrupted: false };
      this.items.push(u);
      this.open[who] = u;
    }
    u.text += piece;
    u.end = t;
    return u;
  }

  close(who, { interrupted = false } = {}) {
    const u = this.open[who];
    if (u) { u.interrupted = interrupted; u.text = u.text.replace(/\s+/g, " ").trim(); }
    this.open[who] = null;
    return u;
  }

  closeAll() { this.close("interviewer"); this.close("candidate"); }

  get turns() { return this.items.filter((u) => u.text.trim()); }

  /* What goes back into a fresh session so the interview continues. */
  asContext() {
    const turns = this.turns;
    if (!turns.length) return "";
    const lines = turns.map((u, i) =>
      `${i + 1}. ${u.who === "interviewer" ? "You (interviewer) said" : "Candidate said"}: ${u.text}${u.interrupted ? " [cut off]" : ""}`);
    while (lines.length && lines.join("\n").length > 40000) lines.shift();
    return "INTERVIEW SO FAR (this same interview, earlier in the call). Continue from here: do not greet again, do not repeat a question already asked, and stay consistent with what was said:\n" + lines.join("\n");
  }
}

export class GeminiLive {
  /**
   * @param {object} o
   * @param {string} o.apiKey            the candidate's own Gemini key
   * @param {function} o.instructions    () => system instruction text (called on every connect)
   * @param {function} [o.getInterviewProgress] () => trusted app-clock snapshot for the read-only pacing tool
   * @param {string} [o.model]
   * @param {string} [o.voice]           prebuilt voice name (Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Zephyr)
   * @param {number} [o.temperature]
   * @param {function} [o.onAudio]       (Int16Array pcm24k) => void
   * @param {function} [o.onInterrupted] () => void
   * @param {function} [o.onTranscript]  (utterance, done) => void   live and final text
   * @param {function} [o.onStatus]      ("connecting"|"live"|"reconnecting"|"failed"|"closed") => void
   * @param {function} [o.onNotice]      (text) => void   human-readable
   * @param {function} [o.onEvent]       (name, data) => void   diagnostics
   */
  constructor(o) {
    this.apiKey = o.apiKey;
    this.instructions = o.instructions;
    this.getInterviewProgress = o.getInterviewProgress;
    this.model = o.model || DEFAULT_MODEL;
    this.voice = o.voice || "";
    this.temperature = o.temperature ?? 0.6;
    this.onAudio = o.onAudio; this.onInterrupted = o.onInterrupted; this.onTranscript = o.onTranscript;
    this.onStatus = o.onStatus; this.onNotice = o.onNotice; this.onEvent = o.onEvent;

    this.transcript = new Transcript();
    this.usage = {};
    this.ws = null;
    this.connected = false;
    this.stopped = false;
    this.sessions = 0;
    this._backoff = 1;
    this._lastServer = 0;
    this._lastVoiced = 0;
    this._connectedAt = 0;
    this._watchdog = null;
    this._modelSpeaking = false;
    this._sendErrors = 0;
    this._now = o.now || now;
    this._retryTimer = null;
    this._goAwayTimer = null;
    this._attemptAt = null;
    this._failures = 0;
    this._resumeHandle = null;
    this._resuming = false;
    this._replyPendingAt = null;
    this._lastOutput = 0;
    this._goAway = false;
    this._playing = false;
    this._activeSince = null;
    this._activeTotal = 0;
    this._lastMicAt = null;
    this._audioEnded = false;
  }

  get healthy() { return this.connected && !this.stopped; }

  get activeSeconds() {
    return this._activeTotal + (this._activeSince === null ? 0 : this._now() - this._activeSince);
  }

  _pauseClock() {
    this._activeTotal = this.activeSeconds;
    this._activeSince = null;
  }

  setPlaying(playing) { this._playing = playing; }

  start() {
    if (this._watchdog) return;
    this.stopped = false;
    this._watchdog = setInterval(() => this._checkStall(), 1000);
    this._connect();
  }

  close() {
    this._pauseClock();
    this.stopped = true;
    this.connected = false;
    clearInterval(this._watchdog);
    this._watchdog = null;
    clearTimeout(this._retryTimer); this._retryTimer = null;
    clearTimeout(this._goAwayTimer); this._goAwayTimer = null;
    const ws = this.ws; this.ws = null;
    if (ws) { try { ws.close(); } catch (_) { /* gone */ } }
    this.transcript.closeAll();
    this._event("session_usage_totals", { usage: { ...this.usage } });
    this._status("closed");
  }

  /* Microphone chunk from AudioIO: 16 kHz Int16 PCM plus its RMS. */
  sendAudio(pcm16, rms) {
    if (!this.healthy) return false;
    const t = this._now();
    this._lastMicAt = t; this._audioEnded = false;
    if (rms >= VOICE_RMS) {
      this._lastVoiced = t;
      if (!this._modelSpeaking && !this._playing) this._replyPendingAt = t;
    }
    // RMS is only a recovery/timing hint, never a noise gate. Quiet words and
    // short answers must reach Gemini with the same samples as louder speech.
    return this._sendJson({ realtimeInput: { audio: {
      data: b64(pcm16.buffer.slice(pcm16.byteOffset, pcm16.byteOffset + pcm16.byteLength)),
      mimeType: `audio/pcm;rate=${CAPTURE_RATE}`,
    } } });
  }

  /* A stage direction the interviewer acts on ("wrap up now"). turnComplete
   * true asks for a reply; false only appends context, like the desktop
   * app's inject_context. */
  sendText(text, { turnComplete = true } = {}) {
    if (!this.healthy) return false;
    if (!this._sendJson({ clientContent: { turns: [{ role: "user", parts: [{ text }] }], turnComplete } })) return false;
    if (turnComplete) this._replyPendingAt = this._now();
    this._event("text_sent", { chars: text.length, turnComplete });
    return true;
  }

  // ------------------------------------------------------------- transport

  _setupMessage() {
    let text = this.instructions();
    const context = this._resumeHandle ? "" : this.transcript.asContext();
    if (context) text += "\n\n" + context;
    if (this.getInterviewProgress) text += "\n\nCURRENT APP CLOCK:\n" + JSON.stringify(this.getInterviewProgress());
    const setup = {
      model: `models/${this.model}`,
      generationConfig: {
        responseModalities: ["AUDIO"],
        temperature: this.temperature,
      },
      systemInstruction: { parts: [{ text }] },
      inputAudioTranscription: {},
      outputAudioTranscription: {},
      sessionResumption: this._resumeHandle ? { handle: this._resumeHandle } : {},
      contextWindowCompression: { slidingWindow: {} },
      realtimeInputConfig: {
        automaticActivityDetection: {
          // Reject tentative speech starts more cautiously, without increasing
          // the minimum speech duration or dropping quiet PCM on the client.
          startOfSpeechSensitivity: "START_SENSITIVITY_LOW",
          prefixPaddingMs: 100,
          // Let soft endings and brief thinking pauses finish before replying.
          endOfSpeechSensitivity: "END_SENSITIVITY_LOW",
          silenceDurationMs: 800,
        },
      },
    };
    if (this.getInterviewProgress) setup.tools = [{ functionDeclarations: [{
      name: "get_interview_progress",
      description: "Read the actual app clock before EVERY spoken turn. Only canWrapUp=true allows the closing stage, unless the candidate explicitly wants to stop. No arguments.",
    }] }];
    if (this.voice) {
      setup.generationConfig.speechConfig = { voiceConfig: { prebuiltVoiceConfig: { voiceName: this.voice } } };
    }
    return { setup };
  }

  _connect() {
    if (this.stopped) return;
    clearTimeout(this._retryTimer); this._retryTimer = null;
    this._attemptAt = this._now();
    this._resuming = !!this._resumeHandle;
    this._status(this.sessions ? "reconnecting" : "connecting");
    let ws;
    try { ws = new WebSocket(LIVE_URL + encodeURIComponent(this.apiKey)); }
    catch (_) { this._event("connect_error", {}); return this._retry(); }
    ws.binaryType = "arraybuffer";
    this.ws = ws;
    ws.onopen = () => {
      if (this.ws !== ws || this.stopped) return;
      this._sendJson(this._setupMessage());
    };
    ws.onmessage = (e) => { if (this.ws === ws && !this.stopped) this._onRaw(e.data, ws); };
    ws.onerror = () => { if (this.ws === ws) this._event("socket_error", {}); };
    ws.onclose = (e) => {
      // A retired socket must never mark its replacement disconnected.
      if (this.ws !== ws || this.stopped) return;
      const wasConnected = this.connected;
      this._disconnect();
      const reason = String(e.reason || "").replaceAll(this.apiKey, "[key]");
      this._event("socket_closed", { code: e.code, reason, wasConnected });
      if (/quota|resource.exhausted|rate.limit|billing/i.test(reason)) {
        return this._fail("Google's usage limit was reached. Check your Gemini quota and try again later. Your answers are kept.");
      }
      if (!wasConnected && this._resuming && /session|resum|handle/i.test(reason)) {
        this._resumeHandle = null;
        this._notice("Restoring the interview from your saved answers…");
        return this._retry();
      }
      if (!wasConnected && /model.*(not found|not supported|unavailable)|not found.*model/i.test(reason)) {
        const next = LIVE_MODELS[LIVE_MODELS.indexOf(this.model) + 1];
        if (next) { this.model = next; this._resumeHandle = null; return this._retry(); }
      }
      if (e.code === 1008 || /invalid.argument|api.key.*(invalid|expired)|permission.denied|unauthenticated|not supported/i.test(reason)) {
        return this._fail(reason || "Google refused this session. Check the API key and its permissions.");
      }
      this._notice("Reconnecting to your interviewer. Your answers are kept and the practice timer is paused.");
      this._retry();
    };
  }

  _disconnect() {
    this._pauseClock();
    this.connected = false;
    this._attemptAt = null;
    this._modelSpeaking = false;
    this._playing = false;
    this._goAway = false;
    clearTimeout(this._goAwayTimer); this._goAwayTimer = null;
    const ws = this.ws; this.ws = null;
    if (ws) { try { ws.close(); } catch (_) { /* already gone */ } }
    if (this.onInterrupted) this.onInterrupted();
    this.transcript.closeAll();
  }

  _reconnect(reason) {
    if (this.stopped) return;
    this._event("reconnect", { reason });
    this._disconnect();
    this._notice("Reconnecting to your interviewer. Your answers are kept and the practice timer is paused.");
    this._retry();
  }

  _fail(message) {
    this._disconnect();
    this.stopped = true;
    clearInterval(this._watchdog); this._watchdog = null;
    clearTimeout(this._retryTimer); this._retryTimer = null;
    this._notice(message);
    this._status("failed");
  }

  _retry() {
    if (this.stopped || this._retryTimer !== null) return;
    if (++this._failures > MAX_RETRIES) {
      return this._fail("The connection could not recover. Your answers are kept. Check your connection and Gemini quota, then try again.");
    }
    this._status(this.sessions ? "reconnecting" : "connecting");
    const wait = this._backoff;
    this._backoff = Math.min(this._backoff * 2, 8);
    this._retryTimer = setTimeout(() => { this._retryTimer = null; this._connect(); }, wait * 1000);
  }

  _sendJson(payload) {
    const ws = this.ws;
    if (!ws || ws.readyState !== WebSocket.OPEN) return false;
    if (ws.bufferedAmount > MAX_BUFFERED_BYTES) { this._reconnect("audio_backpressure"); return false; }
    try { ws.send(JSON.stringify(payload)); return true; }
    catch (_) { this._sendErrors++; this._event("send_error", {}); this._reconnect("send_error"); return false; }
  }

  _checkStall() {
    if (this.stopped) return;
    const t = this._now();
    if (!this.connected) {
      if (this._attemptAt !== null && t - this._attemptAt >= SETUP_TIMEOUT_SECONDS) this._reconnect("setup_timeout");
      return;
    }
    if (this._lastMicAt !== null && t - this._lastMicAt > 1 && !this._audioEnded) {
      this._audioEnded = true;
      this._sendJson({ realtimeInput: { audioStreamEnd: true } });
    }
    if (this._goAway && !this._modelSpeaking && !this._playing && t - this._lastVoiced > 1) {
      this._reconnect("scheduled_refresh"); return;
    }
    // A short answer followed by silence used to fall outside the old
    // "voiced in the last ten seconds" test, leaving the visitor waiting forever.
    const waiting = this._replyPendingAt !== null && t - this._replyPendingAt >= REPLY_TIMEOUT_SECONDS;
    const cutOff = this._modelSpeaking && t - this._lastOutput >= REPLY_TIMEOUT_SECONDS;
    if (!this._playing && (waiting || cutOff)) {
      this._event("stall_detected", { silentFor: Math.round(t - (this._replyPendingAt ?? this._lastOutput)) });
      // A silent generation can also be stuck in the resumable server session.
      // Rebuild it from the transcript instead of resuming that stuck state.
      this._resumeHandle = null;
      this._reconnect("reply_timeout");
    }
  }

  // --------------------------------------------------------------- receive

  async _onRaw(data, ws = this.ws) {
    let text = data;
    if (data instanceof ArrayBuffer) text = new TextDecoder().decode(data);
    else if (data instanceof Blob) text = await data.text();
    if (this.stopped || this.ws !== ws) return;
    let message;
    try { message = JSON.parse(text); } catch { return; }
    this._handle(message);
  }

  _handle(message) {
    const t = this._now();
    this._lastServer = t;
    if (message.toolCall) {
      if (!this.healthy) return;
      const cancelled = new Set(message.toolCallCancellation?.ids || []);
      const functionResponses = (message.toolCall.functionCalls || []).filter(call => !cancelled.has(call.id)).map(call => ({
        id: call.id, name: call.name,
        response: call.name === "get_interview_progress" && this.getInterviewProgress
          ? this.getInterviewProgress() : { error: "Unknown tool. Continue the interview without claiming time is up." },
      }));
      if (functionResponses.length && this._sendJson({ toolResponse: { functionResponses } })) this._replyPendingAt = t;
      return;
    }
    if (message.sessionResumptionUpdate) {
      const update = message.sessionResumptionUpdate;
      this._resumeHandle = update.resumable && update.newHandle ? update.newHandle : null;
    }
    if (message.setupComplete) {
      if (!this.connected) {
        this.connected = true;
        this._attemptAt = null;
        this._connectedAt = t;
        this._lastMicAt = null;
        this._audioEnded = false;
        this.sessions++;
        this._event("connected", { model: this.model, session: this.sessions });
        this._status("live");
        if (this._resuming) {
          // An extra user turn would interrupt the restored conversation.
          this._activeSince = t;
          if (this._replyPendingAt !== null) this._replyPendingAt = t;
        } else {
          const resumed = this.transcript.turns.length > 0;
          this.sendText(resumed ? NOTES.reconnect : NOTES.opening);
        }
      }
      return;
    }
    if (message.goAway) {
      this._event("go_away", { timeLeft: String(message.goAway.timeLeft || "") });
      this._goAway = true;
      clearTimeout(this._goAwayTimer);
      const left = parseFloat(message.goAway.timeLeft);
      this._goAwayTimer = setTimeout(() => this._reconnect("connection_deadline"),
        Math.max(0, (Number.isFinite(left) ? left - 2 : 1)) * 1000);
      return;
    }
    if (message.usageMetadata) {
      const u = message.usageMetadata;
      for (const k of ["promptTokenCount", "responseTokenCount", "totalTokenCount"]) {
        this.usage[k] = (this.usage[k] || 0) + Number(u[k] || 0);
      }
    }
    const content = message.serverContent;
    if (!content) return;

    if (content.interrupted) {
      this._event("interrupted", {});
      const u = this.transcript.close("interviewer", { interrupted: true });
      if (u && this.onTranscript) this.onTranscript(u, true);
      this._modelSpeaking = false;
      if (this.onInterrupted) this.onInterrupted();
    }

    const heard = content.inputTranscription && content.inputTranscription.text;
    if (heard) {
      this._append("candidate", heard, t);
      if (!this._modelSpeaking && !this._playing) this._replyPendingAt = t;
    }

    const said = content.outputTranscription && content.outputTranscription.text;
    if (said) this._append("interviewer", said, t);

    const parts = (content.modelTurn && content.modelTurn.parts) || [];
    for (const part of parts) {
      const inline = part.inlineData;
      if (inline && inline.data && /audio\/pcm/.test(inline.mimeType || "")) {
        this._lastOutput = t;
        this._replyPendingAt = null;
        this._failures = 0; this._backoff = 1;
        if (this._activeSince === null) this._activeSince = t;
        if (!this._modelSpeaking) { this._modelSpeaking = true; this._event("model_audio_start", {}); }
        const buf = unb64(inline.data);
        if (this.onAudio && buf.byteLength >= 2) this.onAudio(new Int16Array(buf.byteLength % 2 ? buf.slice(0, buf.byteLength - 1) : buf));
      } else if (part.text) {
        // A text-mode model would answer here; native audio never does.
        this._append("interviewer", part.text, t);
      }
    }

    if (content.turnComplete) {
      this._modelSpeaking = false;
      const u = this.transcript.close("interviewer");
      if (u && this.onTranscript) this.onTranscript(u, true);
      const c = this.transcript.close("candidate");
      if (c && this.onTranscript) this.onTranscript(c, true);
      this._event("turn_complete", {});
    }
  }

  _append(who, piece, t) {
    const u = this.transcript.append(who, piece, t);
    const closed = this.transcript.justClosed;
    this.transcript.justClosed = null;
    if (closed && closed.text && this.onTranscript) this.onTranscript(closed, true);
    if (this.onTranscript) this.onTranscript(u, false);
  }

  // ------------------------------------------------------------------ misc

  _status(s) { if (this.onStatus) { try { this.onStatus(s); } catch (_) { /* UI */ } } }
  _notice(m) { if (this.onNotice) { try { this.onNotice(m); } catch (_) { /* UI */ } } }
  _event(name, data) { if (this.onEvent) { try { this.onEvent(name, data); } catch (_) { /* UI */ } } }
}

function b64(buffer) {
  const bytes = new Uint8Array(buffer);
  let s = "";
  for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(s);
}

function unb64(text) {
  const s = atob(text);
  const bytes = new Uint8Array(s.length);
  for (let i = 0; i < s.length; i++) bytes[i] = s.charCodeAt(i);
  return bytes.buffer;
}
