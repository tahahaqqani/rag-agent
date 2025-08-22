(function () {
  "use strict";

  // Configuration
  const WIDGET_HOST = new URL(document.currentScript.src).origin;
  const PANEL_URL = WIDGET_HOST + "/widget/chat.html";
  const API_BASE = WIDGET_HOST;

  // Widget state
  let isOpen = false;
  let isInitialized = false;

  // Create unique IDs
  const WIDGET_ID =
    "rag-chat-widget-" + Math.random().toString(36).substr(2, 9);
  const BUTTON_ID = WIDGET_ID + "-button";
  const PANEL_ID = WIDGET_ID + "-panel";

  // CSS styles
  const styles = `
    #${BUTTON_ID} {
      position: fixed;
      right: 20px;
      bottom: 20px;
      z-index: 2147483647;
      border-radius: 50px;
      padding: 12px 20px;
      font-size: 14px;
      font-weight: 600;
      border: none;
      cursor: pointer;
      box-shadow: 0 8px 30px rgba(0,0,0,0.12);
      transition: all 0.3s ease;
      background: #026CBD;
      color: white;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    #${BUTTON_ID}:hover {
      transform: translateY(-2px);
      box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }
    
    #${BUTTON_ID}:active {
      transform: translateY(0);
    }
    
    #${PANEL_ID} {
      position: fixed;
      right: 20px;
      bottom: 80px;
      width: 380px;
      height: 560px;
      max-width: calc(100vw - 40px);
      max-height: calc(100vh - 100px);
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 20px 60px rgba(0,0,0,0.18);
      display: none;
      z-index: 2147483647;
      background: white;
      border: 1px solid #e9ecef;
    }
    
    #${PANEL_ID} iframe {
      width: 100%;
      height: 100%;
      border: 0;
      background: white;
    }
    
    @media (max-width: 480px) {
      #${PANEL_ID} {
        right: 10px;
        left: 10px;
        width: auto;
        height: 70vh;
        bottom: 70px;
      }
      
      #${BUTTON_ID} {
        right: 10px;
        bottom: 10px;
      }
    }
    
    .rag-chat-loading {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      background: #f8f9fa;
      color: #6c757d;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .rag-chat-loading::after {
      content: '';
      width: 20px;
      height: 20px;
      border: 2px solid #e9ecef;
      border-top: 2px solid #026CBD;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-left: 10px;
    }
    
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `;

  // Inject styles
  function injectStyles() {
    if (document.getElementById("rag-chat-styles")) return;

    const styleSheet = document.createElement("style");
    styleSheet.id = "rag-chat-styles";
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
  }

  // Create floating button
  function createButton() {
    const btn = document.createElement("button");
    btn.id = BUTTON_ID;
    btn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="margin-right: 8px;">
        <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
      </svg>
      Chat
    `;

    btn.addEventListener("click", togglePanel);
    return btn;
  }

  // Create chat panel
  function createPanel() {
    const panel = document.createElement("div");
    panel.id = PANEL_ID;

    // Loading state
    panel.innerHTML = `
      <div class="rag-chat-loading">
        Loading chat...
      </div>
    `;

    // Create iframe after a short delay to show loading
    setTimeout(() => {
      const iframe = document.createElement("iframe");
      iframe.src = PANEL_URL;
      iframe.onload = () => {
        // Remove loading state
        panel.innerHTML = "";
        panel.appendChild(iframe);

        // Send message to iframe to initialize
        iframe.contentWindow.postMessage(
          {
            type: "INIT",
            apiBase: API_BASE,
          },
          "*"
        );
      };

      iframe.onerror = () => {
        panel.innerHTML = `
          <div class="rag-chat-loading">
            Failed to load chat. Please refresh the page.
          </div>
        `;
      };
    }, 500);

    return panel;
  }

  // Toggle chat panel
  function togglePanel() {
    if (!isInitialized) {
      isInitialized = true;
      document.body.appendChild(createPanel());
    }

    const panel = document.getElementById(PANEL_ID);
    if (!panel) return;

    isOpen = !isOpen;
    panel.style.display = isOpen ? "block" : "none";

    // Update button text
    const btn = document.getElementById(BUTTON_ID);
    if (btn) {
      btn.innerHTML = isOpen
        ? `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="margin-right: 8px;">
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
        </svg>
        Close
      `
        : `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="margin-right: 8px;">
          <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
        </svg>
        Chat
      `;
    }

    // Focus iframe when opening
    if (isOpen) {
      setTimeout(() => {
        const iframe = panel.querySelector("iframe");
        if (iframe && iframe.contentWindow) {
          iframe.focus();
        }
      }, 100);
    }
  }

  // Close panel when clicking outside
  function handleClickOutside(event) {
    const panel = document.getElementById(PANEL_ID);
    const button = document.getElementById(BUTTON_ID);

    if (
      panel &&
      isOpen &&
      !panel.contains(event.target) &&
      !button.contains(event.target)
    ) {
      togglePanel();
    }
  }

  // Handle escape key
  function handleKeyDown(event) {
    if (event.key === "Escape" && isOpen) {
      togglePanel();
    }
  }

  // Listen for messages from iframe
  function handleMessage(event) {
    if (event.data.type === "CHAT_OPENED") {
      // Handle chat opened event
      console.log("Chat opened");
    } else if (event.data.type === "CHAT_CLOSED") {
      // Handle chat closed event
      console.log("Chat closed");
    }
  }

  // Initialize widget
  function init() {
    // Inject styles
    injectStyles();

    // Create and inject button
    const button = createButton();
    document.body.appendChild(button);

    // Add event listeners
    document.addEventListener("click", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);
    window.addEventListener("message", handleMessage);

    // Log initialization
    console.log("RAG Chat Widget initialized");
  }

  // Auto-initialize when DOM is ready
  if (document.readyState === "complete") {
    init();
  } else {
    window.addEventListener("load", init);
  }

  // Expose widget API globally
  window.RAGChatWidget = {
    open: () => {
      if (!isOpen) togglePanel();
    },
    close: () => {
      if (isOpen) togglePanel();
    },
    toggle: togglePanel,
    isOpen: () => isOpen,
  };
})();
