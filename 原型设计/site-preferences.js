(() => {
  const STORAGE_KEY = "consumerRightsPrefs";
  const DEFAULTS = {
    language: "en",
    fontSize: "medium",
    contrast: "default",
    readingRulerEnabled: false,
    readingRulerColor: "#fef08a",
    readingRulerHeight: "medium"
  };
  let rulerEl = null;
  let rulerMoveHandler = null;
  let rulerLeaveHandler = null;
  let rulerContextMenuHandler = null;
  let rulerKeydownHandler = null;
  const I18N_PAIRS = [
    ["Home", "首页"],
    ["Check my rights", "寻求帮助"],
    ["Start a claim", "提交投诉"],
    ["Contact us", "联系我们"],
    ["User support", "用户支持"],
    ["Accessibility", "无障碍"],
    ["Log in", "登录"],
    ["Sign up", "注册"],
    ["Search", "搜索"],
    ["Need help?", "需要帮助？"],
    ["Phone support", "电话咨询"],
    ["Online support", "在线客服"],
    ["Start chat", "开始聊天"],
    ["Send email", "发送邮件"],
    ["Services", "服务"],
    ["Information", "信息"],
    ["Privacy policy", "隐私政策"],
    ["Terms of use", "使用条款"],
    ["Font size", "字体大小"],
    ["Reading ruler", "阅读标尺"],
    ["Screen reader", "屏幕阅读器"],
    ["Case tracker", "案件追踪"],
    ["Dashboard", "我的面板"],
    ["News", "新闻公告"],
    ["Events", "活动日程"],
    ["Analytics", "数据分析"],
    ["All rights reserved.", "保留所有权利。"],
    ["Previous", "上一页"],
    ["Next", "下一页"],
    ["Close", "关闭"],
    ["Apply", "应用"],
    ["Cancel", "取消"],
    ["Choose Language", "选择语言"],
    ["Back to accessibility menu", "返回无障碍菜单"]
  ];

  function clearReadingRuler() {
    if (rulerMoveHandler) {
      document.removeEventListener("mousemove", rulerMoveHandler);
      rulerMoveHandler = null;
    }
    if (rulerLeaveHandler) {
      document.removeEventListener("mouseleave", rulerLeaveHandler);
      rulerLeaveHandler = null;
    }
    if (rulerContextMenuHandler) {
      document.removeEventListener("contextmenu", rulerContextMenuHandler);
      rulerContextMenuHandler = null;
    }
    if (rulerKeydownHandler) {
      document.removeEventListener("keydown", rulerKeydownHandler);
      rulerKeydownHandler = null;
    }
    if (rulerEl) {
      rulerEl.remove();
      rulerEl = null;
    }
  }

  function enableReadingRuler(prefs) {
    const heightMap = {
      narrow: 28,
      medium: 44,
      wide: 62
    };
    const rulerHeight = heightMap[prefs.readingRulerHeight] || heightMap.medium;

    rulerEl = document.createElement("div");
    rulerEl.className = "reading-ruler-overlay";
    rulerEl.style.position = "fixed";
    rulerEl.style.left = "0";
    rulerEl.style.width = "100%";
    rulerEl.style.height = `${rulerHeight}px`;
    rulerEl.style.pointerEvents = "none";
    rulerEl.style.zIndex = "2147483646";
    rulerEl.style.background = prefs.readingRulerColor || "#fef08a";
    rulerEl.style.opacity = "0";
    rulerEl.style.boxShadow = "0 0 0 1px rgba(17,24,39,0.15)";
    rulerEl.style.transition = "opacity 140ms ease";
    document.body.appendChild(rulerEl);

    rulerMoveHandler = (event) => {
      if (!rulerEl) return;
      rulerEl.style.top = `${event.clientY - rulerHeight / 2}px`;
      rulerEl.style.opacity = "0.35";
    };
    rulerLeaveHandler = () => {
      if (!rulerEl) return;
      rulerEl.style.opacity = "0";
    };
    const disableRuler = () => {
      const next = setPrefs({ readingRulerEnabled: false });
      applyPrefs(next);
    };
    rulerContextMenuHandler = (event) => {
      if (!rulerEl) return;
      event.preventDefault();
      disableRuler();
    };
    rulerKeydownHandler = (event) => {
      if (!rulerEl) return;
      if (event.key === "Escape") {
        disableRuler();
      }
    };
    document.addEventListener("mousemove", rulerMoveHandler);
    document.addEventListener("mouseleave", rulerLeaveHandler);
    document.addEventListener("contextmenu", rulerContextMenuHandler);
    document.addEventListener("keydown", rulerKeydownHandler);
  }

  function getPrefs() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return { ...DEFAULTS, ...(raw ? JSON.parse(raw) : {}) };
    } catch {
      return { ...DEFAULTS };
    }
  }

  function setPrefs(next) {
    const current = getPrefs();
    const merged = { ...current, ...next };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
    return merged;
  }

  function applyPrefs(prefs) {
    const html = document.documentElement;
    const body = document.body;
    if (!body) return;

    const langCode = prefs.language || "en";
    html.lang = langCode;
    html.setAttribute("dir", ["ar", "he", "fa", "ur"].some((c) => langCode.toLowerCase().startsWith(c)) ? "rtl" : "ltr");
    body.classList.remove("contrast-high", "contrast-dark");

    const fontMap = {
      small: "14px",
      medium: "16px",
      large: "18px",
      xlarge: "22px"
    };
    html.style.fontSize = fontMap[prefs.fontSize] || fontMap.medium;

    if (prefs.contrast === "high") body.classList.add("contrast-high");
    if (prefs.contrast === "dark") body.classList.add("contrast-dark");

    clearReadingRuler();
    if (prefs.readingRulerEnabled) {
      enableReadingRuler(prefs);
    }
  }

  function consumeQueryPrefs() {
    const params = new URLSearchParams(window.location.search);
    const patch = {};
    let changed = false;

    if (params.has("lang")) {
      const lang = (params.get("lang") || "en").trim();
      params.delete("lang");
      if (/^[a-zA-Z]{2,3}(-[a-zA-Z0-9]+)*$/.test(lang)) {
        patch.language = lang;
        changed = true;
      }
    }
    if (params.has("font")) {
      const f = params.get("font");
      params.delete("font");
      if (["small", "medium", "large", "xlarge"].includes(f)) {
        patch.fontSize = f;
        changed = true;
      }
    }
    if (params.has("contrast")) {
      patch.contrast = params.get("contrast");
      params.delete("contrast");
      changed = true;
    }
    if (params.has("ruler")) {
      patch.readingRulerEnabled = params.get("ruler") === "on";
      params.delete("ruler");
      changed = true;
    }
    if (params.has("rulerColor")) {
      const color = (params.get("rulerColor") || "").trim();
      if (/^#[0-9a-fA-F]{6}$/.test(color)) {
        patch.readingRulerColor = color;
      }
      params.delete("rulerColor");
      changed = true;
    }
    if (params.has("rulerHeight")) {
      const height = params.get("rulerHeight");
      if (["narrow", "medium", "wide"].includes(height)) {
        patch.readingRulerHeight = height;
      }
      params.delete("rulerHeight");
      changed = true;
    }

    if (changed) {
      const merged = setPrefs(patch);
      applyPrefs(merged);
      localizeByLanguage(merged.language || "en");
      const qs = params.toString();
      const clean = window.location.pathname + (qs ? `?${qs}` : "") + window.location.hash;
      window.history.replaceState({}, "", clean);
    }
  }

  function wireOverlayReturnLinks(selector) {
    const current = window.location.pathname.split("/").pop() || "主页面.html";
    document.querySelectorAll(selector).forEach((a) => {
      const href = a.getAttribute("href");
      if (!href || !href.includes("Overlay -")) return;
      try {
        const url = new URL(href, window.location.href);
        url.searchParams.set("return", current);
        a.setAttribute("href", `${url.pathname.split("/").pop()}?${url.searchParams.toString()}`);
      } catch {
        // no-op
      }
    });
  }

  function wireToolLinksWithReturn() {
    wireOverlayReturnLinks(".subpage-tools-links a.subpage-tool-link");
    wireOverlayReturnLinks('.utility-bar a[href*="Overlay -"]');
  }

  const FONT_ORDER = ["small", "medium", "large", "xlarge"];

  function stepFontSize(delta) {
    const prefs = getPrefs();
    const idx = FONT_ORDER.indexOf(prefs.fontSize || "medium");
    const next = Math.min(FONT_ORDER.length - 1, Math.max(0, idx + delta));
    const value = FONT_ORDER[next];
    applyPrefs(setPrefs({ fontSize: value }));
    localizeByLanguage(getPrefs().language);
    return value;
  }

  function wireUtilityFontSteppers() {
    document.querySelectorAll("[data-font-step]").forEach((btn) => {
      if (btn.dataset.fontStepWired === "1") return;
      btn.dataset.fontStepWired = "1";
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const delta = Number(btn.getAttribute("data-font-step"), 10) || 0;
        if (!delta) return;
        stepFontSize(delta);
      });
    });
  }

  function wireUtilityFontReset() {
    document.querySelectorAll("[data-font-reset]").forEach((btn) => {
      if (btn.dataset.fontResetWired === "1") return;
      btn.dataset.fontResetWired = "1";
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        applyPrefs(setPrefs({ fontSize: "medium" }));
        localizeByLanguage(getPrefs().language);
      });
    });
  }

  function wireUtilityLangDropdown() {
    const wrap = document.querySelector(".utility-la-lang-wrap");
    const btn = document.getElementById("utility-lang-toggle");
    const menu = document.getElementById("utility-lang-menu");
    if (!wrap || !btn || !menu) return;

    const options = Array.from(menu.querySelectorAll(".utility-la-lang-option[data-lang]"));
    const norm = (l) => (l || "").toLowerCase();

    const syncActive = () => {
      const cur = norm(getPrefs().language || "en");
      options.forEach((opt) => {
        const code = norm(opt.getAttribute("data-lang"));
        const match = code === cur;
        opt.classList.toggle("is-active", match);
        opt.setAttribute("aria-selected", match ? "true" : "false");
      });
    };

    const close = () => {
      wrap.classList.remove("is-open");
      menu.hidden = true;
      btn.setAttribute("aria-expanded", "false");
    };

    const open = () => {
      syncActive();
      wrap.classList.add("is-open");
      menu.hidden = false;
      btn.setAttribute("aria-expanded", "true");
    };

    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      if (wrap.classList.contains("is-open")) close();
      else open();
    });

    options.forEach((opt) => {
      opt.addEventListener("click", (e) => {
        e.stopPropagation();
        const lang = opt.getAttribute("data-lang");
        if (lang) window.CR_PREFS.applyPatch({ language: lang });
        syncActive();
        close();
      });
    });

    document.addEventListener("click", (e) => {
      if (!wrap.classList.contains("is-open")) return;
      if (!wrap.contains(e.target)) close();
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && wrap.classList.contains("is-open")) close();
    });

    syncActive();
  }

  window.CR_PREFS = {
    getPrefs,
    setPrefs,
    applyPrefs,
    localizeByLanguage,
    /** Merge partial prefs, persist, apply to page + text direction + optional i18n */
    applyPatch(patch) {
      const merged = setPrefs(patch);
      applyPrefs(merged);
      localizeByLanguage(merged.language || "en");
      return merged;
    },
    stepFontSize
  };

  function wireListenButton() {
    const listenBtns = Array.from(document.querySelectorAll(".subpage-listen-btn, .home-listen-btn"));
    if (!listenBtns.length) return;

    const synth = window.speechSynthesis;
    if (!synth || typeof window.SpeechSynthesisUtterance === "undefined") return;

    let speaking = false;
    let paused = false;
    let activeBtn = null;

    const getReadableText = () => {
      const main = document.querySelector("main");
      const source = main || document.body;
      return (source.innerText || "")
        .replace(/\s+/g, " ")
        .replace(/Previous Next/g, "")
        .trim();
    };

    const setButtonState = (isSpeaking, isPaused = false, btn = activeBtn) => {
      speaking = isSpeaking;
      paused = isPaused;
      if (btn) {
        const label = btn.dataset.listenLabel || "Listen";
        btn.textContent = label;
        btn.classList.toggle("is-speaking", isSpeaking && !isPaused);
      }
    };

    listenBtns.forEach((listenBtn) => {
      listenBtn.dataset.listenLabel = (listenBtn.textContent || "Listen").trim() || "Listen";
      listenBtn.textContent = listenBtn.dataset.listenLabel;

      listenBtn.addEventListener("click", (e) => {
        e.preventDefault();

        if (speaking && activeBtn !== listenBtn) {
          synth.cancel();
          setButtonState(false, false, activeBtn);
          activeBtn = null;
        }

        if (speaking && activeBtn === listenBtn && !paused) {
          synth.pause();
          setButtonState(true, true, listenBtn);
          return;
        }

        if (speaking && activeBtn === listenBtn && paused) {
          synth.resume();
          setButtonState(true, false, listenBtn);
          return;
        }

        const text = getReadableText();
        if (!text) return;

        synth.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = document.documentElement.lang || "en";
        utterance.rate = 1;
        utterance.pitch = 1;
        utterance.onend = () => {
          setButtonState(false, false, activeBtn);
          activeBtn = null;
        };
        utterance.onerror = () => {
          setButtonState(false, false, activeBtn);
          activeBtn = null;
        };

        activeBtn = listenBtn;
        setButtonState(true, false, listenBtn);
        synth.speak(utterance);
      });
    });

    window.addEventListener("beforeunload", () => {
      synth.cancel();
      setButtonState(false, false, activeBtn);
      activeBtn = null;
    });
  }

  function wireVoiceSearch() {
    const searchInputs = Array.from(
      document.querySelectorAll(".subpage-search input[type='search'], .search-bar input[type='search']")
    );

    const modal = document.createElement("div");
    modal.className = "voice-modal-backdrop";
    modal.innerHTML = `
      <div class="voice-modal" role="dialog" aria-modal="true" aria-label="Voice input dialog">
        <div class="voice-modal-top">
          <button type="button" class="voice-modal-close" aria-label="Close voice input">✕</button>
        </div>
        <div class="voice-modal-content">
          <div>
            <p class="voice-modal-title">Please state what you want to search for</p>
            <p class="voice-modal-live" id="voice-live-text"></p>
          </div>
          <div class="voice-modal-mic-circle" aria-hidden="true">
            <svg class="voice-modal-mic-icon" viewBox="0 0 64 64" aria-hidden="true" focusable="false">
              <path d="M32 42a11 11 0 0 0 11-11V15a11 11 0 1 0-22 0v16a11 11 0 0 0 11 11zm0 6c-10.5 0-19-8.5-19-19a3 3 0 0 1 6 0c0 7.2 5.8 13 13 13s13-5.8 13-13a3 3 0 0 1 6 0c0 10.5-8.5 19-19 19zm-3 6h6v7h11a3 3 0 1 1 0 6H18a3 3 0 1 1 0-6h11v-7z"/>
            </svg>
          </div>
        </div>
        <div class="voice-modal-actions">
          <button type="button" class="voice-modal-btn" data-action="cancel">Cancel</button>
          <button type="button" class="voice-modal-btn primary" data-action="confirm">Confirm</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    let activeInput = null;
    let transcript = "";
    let recognition = null;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const liveText = modal.querySelector("#voice-live-text");

    if (SpeechRecognition) {
      recognition = new SpeechRecognition();
      recognition.lang = document.documentElement.lang || "en-US";
      recognition.interimResults = true;
      recognition.continuous = false;

      recognition.onresult = (event) => {
        transcript = Array.from(event.results)
          .map((r) => r[0].transcript)
          .join(" ")
          .trim();
        liveText.textContent = transcript;
      };
    }

    const openModal = (input) => {
      activeInput = input;
      transcript = "";
      liveText.textContent = "";
      modal.classList.add("open");
      document.body.style.overflow = "hidden";
      if (recognition) {
        try { recognition.start(); } catch {}
      } else {
        liveText.textContent = "Voice input is not supported in this browser.";
      }
    };
    window.openVoiceInputModalFor = openModal;

    const closeModal = () => {
      if (recognition) {
        try { recognition.stop(); } catch {}
      }
      modal.classList.remove("open");
      document.body.style.overflow = "";
    };

    modal.querySelector(".voice-modal-close").addEventListener("click", closeModal);
    modal.querySelector("[data-action='cancel']").addEventListener("click", closeModal);
    modal.querySelector("[data-action='confirm']").addEventListener("click", () => {
      if (activeInput && transcript) {
        activeInput.value = transcript;
        activeInput.dispatchEvent(new Event("input", { bubbles: true }));
      }
      if (activeInput) {
        const assistantPanel = activeInput.closest(".floating-ai-assistant")?.querySelector(".floating-ai-panel");
        if (assistantPanel) {
          assistantPanel.classList.add("open");
          activeInput.focus();
        }
      }
      closeModal();
    });

    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeModal();
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && modal.classList.contains("open")) {
        closeModal();
      }
    });

    searchInputs.forEach((input) => {
      if (input.dataset.voiceWired === "1") return;
      if (!input.parentNode) return;
      input.dataset.voiceWired = "1";

      const wrap = document.createElement("div");
      wrap.className = "search-input-wrap";
      input.parentNode.insertBefore(wrap, input);
      wrap.appendChild(input);

      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "voice-search-trigger";
      btn.setAttribute("aria-label", "Voice input");
      btn.innerHTML = `
        <svg viewBox="0 0 64 64" aria-hidden="true" focusable="false">
          <path d="M32 42a11 11 0 0 0 11-11V15a11 11 0 1 0-22 0v16a11 11 0 0 0 11 11zm0 6c-10.5 0-19-8.5-19-19a3 3 0 0 1 6 0c0 7.2 5.8 13 13 13s13-5.8 13-13a3 3 0 0 1 6 0c0 10.5-8.5 19-19 19zm-3 6h6v7h11a3 3 0 1 1 0 6H18a3 3 0 1 1 0-6h11v-7z"/>
        </svg>
      `;
      wrap.appendChild(btn);

      btn.addEventListener("click", () => openModal(input));
    });
  }

  function wireEnterToConfirm() {
    document.addEventListener("keydown", (event) => {
      if (event.defaultPrevented || event.key !== "Enter") return;
      const target = event.target;
      if (!(target instanceof HTMLInputElement)) return;
      if (target.type === "file" || target.type === "checkbox" || target.type === "radio") return;
      if (target.closest(".chatbot-input")) return;

      const form = target.closest("form");
      if (!form) return;
      event.preventDefault();

      const submitLikeButton =
        form.querySelector("button[type='submit']") ||
        form.querySelector("input[type='submit']") ||
        form.querySelector("button.btn-primary");

      if (submitLikeButton) {
        submitLikeButton.click();
        return;
      }

      if (typeof form.requestSubmit === "function") {
        form.requestSubmit();
      } else {
        form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
      }
    });
  }

  const FLOATING_AI_BUTTON_HTML = `
      <button type="button" class="floating-ai-trigger" aria-label="Contact our AI assistant" title="Contact our AI assistant">
        <span class="floating-ai-glyph-wrap" aria-hidden="true">
          <span class="floating-ai-emoji" aria-hidden="true">🤖</span>
          <span class="floating-ai-label">Contact our<br>AI assistant</span>
        </span>
      </button>`;

  function wireFloatingAiAssistant() {
    const prior = document.getElementById("floating-ai-assistant");
    if (prior && prior.getAttribute("data-floating-ai-rev") === "6") {
      return;
    }
    if (prior) {
      prior.remove();
    }
    if (!document.body) {
      return;
    }

    const root = document.createElement("div");
    root.id = "floating-ai-assistant";
    root.className = "floating-ai-assistant";
    root.setAttribute("data-floating-ai-rev", "6");
    root.innerHTML = `
      ${FLOATING_AI_BUTTON_HTML}
      <div class="floating-ai-panel" role="dialog" aria-modal="false" aria-label="AI legal chatbot panel">
        <div class="floating-ai-panel-top">
          <button type="button" class="floating-ai-close" aria-label="Close chatbot">×</button>
        </div>
        <div class="floating-ai-body">
          <p class="title">Hi there! I'm your AI legal helper.</p>
          <p>I'm here to help with your consumer questions.</p>
          <p style="margin-top:0.55rem;"><strong>Frequently Asked Questions:</strong></p>
          <ul>
            <li>What are my rights as a consumer?</li>
            <li>How can I report a problem to a business?</li>
            <li><a href="任务 1 主页面.html">Can I get my money back?</a></li>
            <li>What if I cannot afford legal costs?</li>
          </ul>
        </div>
        <div class="floating-ai-spacer"></div>
        <div class="floating-ai-input-wrap">
          <input type="text" class="floating-ai-input" placeholder="Input your question here">
          <button type="button" class="floating-ai-mini-btn floating-ai-voice-btn" aria-label="Voice input">
            <svg viewBox="0 0 64 64" aria-hidden="true" focusable="false">
              <path d="M32 42a11 11 0 0 0 11-11V15a11 11 0 1 0-22 0v16a11 11 0 0 0 11 11zm0 6c-10.5 0-19-8.5-19-19a3 3 0 0 1 6 0c0 7.2 5.8 13 13 13s13-5.8 13-13a3 3 0 0 1 6 0c0 10.5-8.5 19-19 19zm-3 6h6v7h11a3 3 0 1 1 0 6H18a3 3 0 1 1 0-6h11v-7z"/>
            </svg>
          </button>
          <button type="button" class="floating-ai-mini-btn send" aria-label="Send message">➜</button>
        </div>
      </div>
    `;
    document.body.appendChild(root);

    const trigger = root.querySelector(".floating-ai-trigger");
    const panel = root.querySelector(".floating-ai-panel");
    const closeBtn = root.querySelector(".floating-ai-close");
    const input = root.querySelector(".floating-ai-input");
    const voiceBtn = root.querySelector(".floating-ai-voice-btn");
    const sendBtn = root.querySelector(".floating-ai-mini-btn.send");
    const body = root.querySelector(".floating-ai-body");

    const openPanel = () => panel.classList.add("open");
    const closePanel = () => panel.classList.remove("open");
    const togglePanel = () => panel.classList.toggle("open");

    const appendReply = (text) => {
      const p = document.createElement("p");
      p.style.marginTop = "0.55rem";
      p.textContent = text;
      body.appendChild(p);
    };

    const send = () => {
      const q = (input.value || "").trim();
      if (!q) return;
      appendReply(`You: ${q}`);
      input.value = "";
      appendReply("AI: Thanks, I can help you with claim steps, case tracking, and contacting support.");
    };

    const hasBlockingOverlay = () => {
      const overlays = Array.from(document.querySelectorAll(".overlay-backdrop, .voice-modal-backdrop"));
      return overlays.some((el) => {
        if (el.classList.contains("voice-modal-backdrop")) {
          return el.classList.contains("open");
        }
        const style = window.getComputedStyle(el);
        return style.display !== "none" && style.visibility !== "hidden" && style.opacity !== "0";
      });
    };

    const syncInteractivity = () => {
      root.classList.toggle("disabled", hasBlockingOverlay());
    };

    trigger.addEventListener("click", togglePanel);
    closeBtn.addEventListener("click", closePanel);
    voiceBtn.addEventListener("click", () => {
      if (typeof window.openVoiceInputModalFor === "function") {
        window.openVoiceInputModalFor(input);
      }
    });
    sendBtn.addEventListener("click", send);
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        send();
      }
    });

    document.addEventListener("click", (e) => {
      if (!panel.classList.contains("open")) return;
      if (e.target.closest(".voice-modal-backdrop")) return;
      if (!root.contains(e.target)) closePanel();
    });

    const observer = new MutationObserver(syncInteractivity);
    observer.observe(document.body, { attributes: true, childList: true, subtree: true, attributeFilter: ["class", "style"] });
    syncInteractivity();
  }

  function wireGlobalChatFab() {
    if (!document.body) {
      return;
    }
    if (document.getElementById("global-la-chat-fab")) {
      return;
    }
    document.querySelectorAll("a.la-chat-fab:not(#global-la-chat-fab)").forEach((el) => el.remove());
    const a = document.createElement("a");
    a.id = "global-la-chat-fab";
    a.className = "la-chat-fab";
    a.href = "Overlay - Chatbot.html";
    a.innerHTML = 'Chat with us <span class="la-chat-ico" aria-hidden="true">💬</span>';
    document.body.appendChild(a);
  }

  function localizeByLanguage(lang) {
    const code = (lang || "en").toLowerCase();
    const isChinese = code.startsWith("zh");
    const map = new Map();
    I18N_PAIRS.forEach(([en, zh]) => {
      map.set(isChinese ? en : zh, isChinese ? zh : en);
    });

    const replaceText = (value) => {
      if (!value || typeof value !== "string") return value;
      let next = value;
      map.forEach((to, from) => {
        if (next.includes(from)) next = next.split(from).join(to);
      });
      return next;
    };

    document.title = replaceText(document.title);

    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const textNodes = [];
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (!node || !node.parentElement) continue;
      const tag = node.parentElement.tagName;
      if (tag === "SCRIPT" || tag === "STYLE") continue;
      textNodes.push(node);
    }
    textNodes.forEach((node) => {
      const replaced = replaceText(node.nodeValue);
      if (replaced !== node.nodeValue) node.nodeValue = replaced;
    });

    const attrNodes = document.querySelectorAll("[placeholder], [aria-label], [title]");
    attrNodes.forEach((el) => {
      ["placeholder", "aria-label", "title"].forEach((attr) => {
        const oldVal = el.getAttribute(attr);
        if (!oldVal) return;
        const replaced = replaceText(oldVal);
        if (replaced !== oldVal) el.setAttribute(attr, replaced);
      });
    });
  }

  function runSafe(label, fn) {
    try {
      fn();
    } catch (err) {
      console.error(`[site-preferences] ${label}`, err);
    }
  }

  function bootSitePreferences() {
    consumeQueryPrefs();
    const prefs = getPrefs();
    applyPrefs(prefs);
    localizeByLanguage(prefs.language);
    runSafe("wireToolLinksWithReturn", wireToolLinksWithReturn);
    runSafe("wireUtilityFontSteppers", wireUtilityFontSteppers);
    runSafe("wireUtilityFontReset", wireUtilityFontReset);
    runSafe("wireUtilityLangDropdown", wireUtilityLangDropdown);
    runSafe("wireListenButton", wireListenButton);
    runSafe("wireVoiceSearch", wireVoiceSearch);
    runSafe("wireEnterToConfirm", wireEnterToConfirm);
  }

  document.addEventListener("DOMContentLoaded", () => {
    runSafe("wireFloatingAiAssistant", wireFloatingAiAssistant);
    runSafe("wireGlobalChatFab", wireGlobalChatFab);
    runSafe("bootSitePreferences", bootSitePreferences);
  });

  window.addEventListener("load", () => {
    if (!document.getElementById("floating-ai-assistant")) {
      runSafe("wireFloatingAiAssistant(fallback)", wireFloatingAiAssistant);
    }
    if (!document.getElementById("global-la-chat-fab")) {
      runSafe("wireGlobalChatFab(fallback)", wireGlobalChatFab);
    }
  });
})();
