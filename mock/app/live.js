/* Prep Sarthi: Gemini Live as the interviewer, in the browser.
 *
 * A line-by-line port of the desktop app's gemini_realtime_live.py with the
 * roles flipped. Same BidiGenerateContent websocket, same setup message
 * (native-audio models only answer as speech, so audio is requested and both
 * transcriptions are switched on), same stall watchdog and the same
 * reconnect-with-memory approach: Gemini forgets everything on a new session,
 * so we keep the transcript ourselves and put it back into the next session's
 * system instruction.
 *
 * What is different from the desktop engine:
 *   - the audio Gemini sends back is played (there it was discarded)
 *   - the microphone is the only input (there it was the meeting audio)
 *   - inputTranscription is what the CANDIDATE said, outputTranscription is
 *     what the INTERVIEWER said
 *   - `interrupted` clears the speaker queue (barge-in)
 *   - after each connect the interviewer is nudged to speak first
 *
 * Everything the page needs arrives through callbacks; nothing here touches
 * the DOM. Only the Gemini key the user pasted is ever sent, and only to
 * Google.
 */

// The desktop app's proven model first; the non-preview one if Google retires it.
export const LIVE_MODELS = ["gemini-3.1-flash-live-preview", "gemini-3.8-live"];
export const DEFAULT_MODEL = LIVE_MODELS[0];
const LIVE_URL = "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key=";
const CAPTURE_RATE = 16000;

// Measured on the desktop app (2026-08-23, free tier): the server goes silently
// mute mid-session, no error, no goAway. A fresh session restores service.
const STALL_SECONDS = 25;
const STALL_GRACE_AFTER_CONNECT = 30;
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
  }

  get healthy() { return this.connected && !this.stopped; }

  start() {
    this.stopped = false;
    this._watchdog = setInterval(() => this._checkStall(), 1000);
    this._connect();
  }

  close() {
    this.stopped = true;
    this.connected = false;
    clearInterval(this._watchdog);
    const ws = this.ws; this.ws = null;
    if (ws) { try { ws.close(); } catch (_) { /* gone */ } }
    this.transcript.closeAll();
    this._event("session_usage_totals", { usage: { ...this.usage } });
    this._status("closed");
  }

  /* Microphone chunk from AudioIO: 16 kHz Int16 PCM plus its RMS. */
  sendAudio(pcm16, rms) {
    if (!this.healthy) return false;
    if (rms >= VOICE_RMS) this._lastVoiced = now();
    this._sendJson({ realtimeInput: { audio: { data: b64(pcm16.buffer), mimeType: `audio/pcm;rate=${CAPTURE_RATE}` } } });
    return true;
  }

  /* A stage direction the interviewer acts on ("wrap up now"). turnComplete
   * true asks for a reply; false only appends context, like the desktop
   * app's inject_context. */
  sendText(text, { turnComplete = true } = {}) {
    if (!this.healthy) return false;
    this._sendJson({ clientContent: { turns: [{ role: "user", parts: [{ text }] }], turnComplete } });
    this._event("text_sent", { chars: text.length, turnComplete });
    return true;
  }

  // ------------------------------------------------------------- transport

  _setupMessage() {
    let text = this.instructions();
    const context = this.transcript.asContext();
    if (context) text += "\n\n" + context;
    const setup = {
      model: `models/${this.model}`,
      generationConfig: {
        responseModalities: ["AUDIO"],
        temperature: this.temperature,
      },
      systemInstruction: { parts: [{ text }] },
      inputAudioTranscription: {},
      outputAudioTranscription: {},
    };
    if (this.voice) {
      setup.generationConfig.speechConfig = { voiceConfig: { prebuiltVoiceConfig: { voiceName: this.voice } } };
    }
    return { setup };
  }

  _connect() {
    if (this.stopped) return;
    this._status(this.sessions ? "reconnecting" : "connecting");
    let ws;
    try {
      ws = new WebSocket(LIVE_URL + encodeURIComponent(this.apiKey));
    } catch (err) {
      this._event("connect_error", { error: String(err) });
      return this._retry();
    }
    ws.binaryType = "arraybuffer";
    this.ws = ws;
    ws.onopen = () => {
      this._backoff = 1;
      this._sendJson(this._setupMessage());
    };
    ws.onmessage = (e) => this._onRaw(e.data);
    ws.onerror = () => this._event("socket_error", {});
    ws.onclose = (e) => {
      const wasConnected = this.connected;
      this.connected = false;
      if (this.ws === ws) this.ws = null;
      this._event("socket_closed", { code: e.code, reason: e.reason, wasConnected });
      // A half-spoken turn must not hang open.
      this.transcript.closeAll();
      if (this.stopped) return;
      // Google explains a refusal in the close reason (bad key, billing,
      // quota, model name). Retrying that forever only hides the message.
      if (!wasConnected && e.reason) {
        this._event("refused", { code: e.code, reason: e.reason, model: this.model });
        // A retired model name is Google's problem, not the user's: try the next one.
        const next = LIVE_MODELS[LIVE_MODELS.indexOf(this.model) + 1];
        if (next && /model|not found|not supported|unavailable/i.test(e.reason)) {
          this._notice(`Switching to ${next}`);
          this.model = next;
          return this._retry();
        }
        this.stopped = true;
        clearInterval(this._watchdog);
        this._notice(e.reason);
        this._status("failed");
        return;
      }
      this._notice(wasConnected ? "Connection to Gemini dropped, reconnecting" : "Gemini unreachable, retrying");
      this._retry();
    };
  }

  _retry() {
    if (this.stopped) return;
    const wait = this._backoff;
    this._backoff = Math.min(this._backoff * 2, 15);
    setTimeout(() => this._connect(), wait * 1000);
  }

  _sendJson(payload) {
    const ws = this.ws;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    try { ws.send(JSON.stringify(payload)); }
    catch (err) { this._sendErrors++; this._event("send_error", { error: String(err) }); }
  }

  _checkStall() {
    const t = now();
    if (!this.connected
      || t - this._connectedAt < STALL_GRACE_AFTER_CONNECT
      || t - this._lastVoiced > 10
      || t - this._lastServer < STALL_SECONDS) return;
    this._event("stall_detected", { silentFor: Math.round(t - this._lastServer) });
    this._notice("Gemini went quiet, reconnecting");
    this.connected = false;
    const ws = this.ws;
    if (ws) { try { ws.close(); } catch (_) { /* reconnect path */ } }
  }

  // --------------------------------------------------------------- receive

  async _onRaw(data) {
    let text = data;
    if (data instanceof ArrayBuffer) text = new TextDecoder().decode(data);
    else if (data instanceof Blob) text = await data.text();
    let message;
    try { message = JSON.parse(text); } catch { return; }
    this._handle(message);
  }

  _handle(message) {
    const t = now();
    this._lastServer = t;
    if (message.setupComplete) {
      if (!this.connected) {
        this.connected = true;
        this._connectedAt = t;
        this.sessions++;
        this._event("connected", { model: this.model, session: this.sessions });
        this._status("live");
        // The interviewer speaks first. On a reconnect it picks up mid-interview.
        const resumed = this.transcript.turns.length > 0;
        this.sendText(resumed
          ? "(The call reconnected. Continue the interview from exactly where it stopped: no greeting, no recap, just your next question or follow-up.)"
          : "(The candidate has just joined the call. Greet them briefly and begin.)");
      }
      return;
    }
    if (message.goAway) {
      this._event("go_away", { timeLeft: String(message.goAway.timeLeft || "") });
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
    if (heard) this._append("candidate", heard, t);

    const said = content.outputTranscription && content.outputTranscription.text;
    if (said) this._append("interviewer", said, t);

    const parts = (content.modelTurn && content.modelTurn.parts) || [];
    for (const part of parts) {
      const inline = part.inlineData;
      if (inline && inline.data && /audio\/pcm/.test(inline.mimeType || "")) {
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
