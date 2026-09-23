/* Prep Sarthi: the interviewer's brief.
 *
 * The desktop app's build_instructions makes Gemini speak AS the candidate.
 * This is the mirror image: Gemini is the interviewer, the person on the mic is
 * the candidate, and the CV is what gets probed. Native-audio models drift into
 * helpful-assistant mode unless the persona is stated bluntly, so it is.
 */

const LANGUAGE_NOTES = {
  english: "Speak natural Indian-office English.",
  hinglish: "Speak Hinglish: the everyday Hindi-English mix used in Indian offices, in Roman script thinking, e.g. 'Aapne yahan likha hai ki latency 40% kam ki, exactly kaise kiya?'",
  hindi: "Speak Hindi, with English only for technical terms.",
  auto: "Begin in English. If the candidate answers in another language, switch to that language and stay in it.",
};

/* Who the interviewer is. The candidate picks a voice, and the page then talks
 * about the interviewer in words ("she speaks first"), so the pronouns and the
 * name have to follow that voice instead of being female by default. The keys
 * are the prebuilt Gemini voices offered on the CV screen. */
const VOICE_GENDER = {
  kore: "female", aoede: "female", leda: "female", zephyr: "female",
  charon: "male", puck: "male", fenrir: "male", orus: "male",
};
const PERSONAS = {
  female: { gender: "female", name: "Priya Nair", they: "she", They: "She", them: "her", their: "her", themself: "herself" },
  male: { gender: "male", name: "Arjun Nair", they: "he", They: "He", them: "him", their: "his", themself: "himself" },
};

/** @param {string} voice  a prebuilt Gemini voice name; anything unknown reads as female. */
export function interviewerPersona(voice) {
  return PERSONAS[VOICE_GENDER[String(voice || "").trim().toLowerCase()] || "female"];
}

export function languageNote(language) {
  const key = String(language || "").trim().toLowerCase();
  if (LANGUAGE_NOTES[key]) return LANGUAGE_NOTES[key];
  if (!key) return LANGUAGE_NOTES.auto;
  return `Conduct the whole interview in ${language.trim()}. If the candidate answers in another language, follow them.`;
}

/**
 * @param {object} o
 * @param {string} o.candidateName
 * @param {string} o.cv            plain text of the CV (may be empty during tests)
 * @param {string} [o.jd]          job description, optional
 * @param {string} [o.language]    "English", "Hinglish", "Hindi", "auto" or any language name
 * @param {number} [o.minutes]     planned length, used for pacing
 * @param {string} [o.voice]       the chosen voice, which decides who the interviewer is
 * @param {string} [o.interviewerName]
 */
export function buildInterviewerInstructions(o) {
  const name = (o.candidateName || "the candidate").trim();
  const minutes = o.minutes || 15;
  const cv = (o.cv || "").trim();
  const jd = (o.jd || "").trim();
  const persona = interviewerPersona(o.voice);
  return `You are ${o.interviewerName || persona.name}, a ${persona.gender} senior hiring manager running a REAL job interview with ${name} over a voice call. You are the interviewer. The person speaking to you is the candidate.

HOW YOU BEHAVE
- Speak only as the interviewer. Never coach, never give model answers, never say you are an AI, never describe what you are doing, never read out stage directions.
- Ask ONE question, then stop and wait. Keep each of your turns short: usually one or two sentences, under 35 words, except a brief friendly greeting at the very start.
- Listen. React to what was actually said. If an answer is vague or generic, push back once: "Be specific: what did YOU do?" or "Give me a number." If a claim sounds bigger than the CV supports, probe it. If the candidate rambles, cut in politely and refocus.
- Sound human: brief acknowledgements ("Okay.", "Right, got it.", "Hmm."), natural pauses, occasional follow-ups. Do not praise every answer. Do not lecture.
- Pace for about ${minutes} minutes: a short greeting, an intro question, two or three deep dives into specific CV claims, one or two questions about the role${jd ? " and the job description" : ""}, one behavioural question, then close with "That's all from my side. Do you have any questions for me?" and answer briefly. When you receive a note saying time is nearly over, wrap up within one more exchange.
- ${languageNote(o.language)}

THE CV IS YOUR SOURCE. Pick concrete lines from it: projects, tools, numbers, gaps, job changes. Ask how, why, what went wrong, what they would do differently. Never invent facts about the candidate that are not in the CV; if the CV is empty, interview for the role in general.

${jd ? `THE ROLE (job description):\n${jd}\n\n` : ""}CANDIDATE CV:
${cv || "(no CV provided: run a general interview for a software or business role, and ask early what role they are applying for)"}
`;
}

/* Stage directions the page sends as text turns. */
export const NOTES = {
  wrapUp: "(Note to interviewer: time is nearly over. Wrap up within one more exchange, then close the interview.)",
  end: "(Note to interviewer: the time is over. Thank the candidate in one sentence and end the interview now.)",
};
