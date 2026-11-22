/* SHOHIN AI shared browser client.
   Set window.SHOHIN_AI_ENDPOINT before loading this file.
   No private server credentials belong in browser code. */
(function (root) {
  "use strict";

  const PROFILES = Object.freeze({
    english: { appId: "english", label: "SHOHIN ENGLISH" },
    tajikChinese: { appId: "tajik-chinese", label: "SHOHIN TAJIK–CHINESE" },
    dictionary: { appId: "dictionary", label: "SHOHIN DICTIONARY" },
    weather: { appId: "weather", label: "SHOHIN WEATHER" },
    generic: { appId: "generic", label: "SHOHIN AI" }
  });

  async function chat(options) {
    const opts = options || {};
    const endpoint = String(root.SHOHIN_AI_ENDPOINT || "").replace(/\/+$/, "");
    if (!endpoint) throw new Error("SHOHIN AI server URL is not configured.");
    const profile = opts.profile || "generic";
    const selected = PROFILES[profile] || PROFILES.generic;
    if (!Array.isArray(opts.messages) || opts.messages.length === 0) {
      throw new Error("At least one chat message is required.");
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), opts.timeoutMs || 90000);
    try {
      const response = await fetch(endpoint + "/v1/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
        body: JSON.stringify({
          app_id: selected.appId,
          language: opts.language || "auto",
          app_context: String(opts.context || "").slice(0, 3000),
          messages: opts.messages.slice(-16).map(function (m) {
            return {
              role: m.role === "assistant" ? "assistant" : "user",
              content: String(m.content || "").slice(0, 6000)
            };
          })
        })
      });

      let data = {};
      try { data = await response.json(); } catch (_) {}
      if (!response.ok) {
        const message = data.detail || ("HTTP " + response.status);
        throw new Error(String(message));
      }
      if (!data.answer) throw new Error("SHOHIN AI returned an empty answer.");
      return data;
    } catch (error) {
      if (error && error.name === "AbortError") {
        throw new Error("SHOHIN AI server timed out. Try again.");
      }
      throw error;
    } finally {
      clearTimeout(timeout);
    }
  }

  root.SHOHIN_AI = Object.freeze({ profiles: PROFILES, chat: chat });
})(window);
