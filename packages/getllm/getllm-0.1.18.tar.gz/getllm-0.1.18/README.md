# getllm

getllm is a Python package for managing LLM models with Ollama integration and generating Python code. It allows you to install, list, set the default model, update the model list, and generate code using LLM models. GetLLM is part of the PyLama ecosystem and integrates with LogLama as the primary service for centralized logging and environment management.

<svg width="1200" height="800" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
    
    <linearGradient id="cardGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#f7fafc;stop-opacity:1" />
    </linearGradient>
    
    <linearGradient id="textGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
    
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge> 
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    
    <filter id="shadow">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.1"/>
    </filter>
  </defs>
  
  <!-- Tło -->
  <rect width="1200" height="800" fill="url(#bgGradient)"/>
  
  <!-- Animowane particles w tle -->
  <g id="particles">
    <circle r="3" fill="rgba(255,255,255,0.3)">
      <animateMotion dur="15s" repeatCount="indefinite" 
                     path="M 100,100 Q 600,200 1100,150 T 100,100"/>
    </circle>
    <circle r="2" fill="rgba(255,255,255,0.2)">
      <animateMotion dur="12s" repeatCount="indefinite" 
                     path="M 200,300 Q 700,100 900,600 T 200,300"/>
    </circle>
    <circle r="2.5" fill="rgba(255,255,255,0.25)">
      <animateMotion dur="18s" repeatCount="indefinite" 
                     path="M 800,50 Q 300,400 100,700 T 800,50"/>
    </circle>
  </g>
  
  <!-- Slajd 1: Tytuł -->
  <g id="slide1">
    <!-- Główna karta -->
    <rect x="100" y="100" width="1000" height="600" rx="20" fill="url(#cardGradient)" 
          filter="url(#shadow)" opacity="0">
      <animate attributeName="opacity" values="0;1" dur="1s" fill="freeze"/>
    </rect>
    
    <!-- Logo animowane -->
    <text x="600" y="220" text-anchor="middle" font-family="Arial, sans-serif" 
          font-size="80" font-weight="bold" fill="url(#textGradient)" filter="url(#glow)">
      getllm
      <animate attributeName="font-size" values="60;80;60" dur="3s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;1" dur="1.5s" fill="freeze"/>
    </text>
    
    <!-- Podtytuł -->
    <text x="600" y="280" text-anchor="middle" font-family="Arial, sans-serif" 
          font-size="24" fill="#4a5568" opacity="0">
      Zarządzanie modelami LLM z integracją Ollama
      <animate attributeName="opacity" values="0;1" dur="1s" begin="1s" fill="freeze"/>
    </text>
    
    <!-- Opis -->
    <text x="600" y="320" text-anchor="middle" font-family="Arial, sans-serif" 
          font-size="18" fill="#718796" opacity="0">
      Python package dla efektywnego zarządzania modelami AI
      <animate attributeName="opacity" values="0;1" dur="1s" begin="2s" fill="freeze"/>
    </text>
    
    <!-- Ikony funkcji -->
    <g id="feature-icons" opacity="0">
      <animate attributeName="opacity" values="0;1" dur="1s" begin="3s" fill="freeze"/>
      
      <!-- Kod -->
      <rect x="200" y="400" width="120" height="80" rx="10" fill="#667eea" opacity="0.8">
        <animate attributeName="y" values="420;400;420" dur="2s" repeatCount="indefinite"/>
      </rect>
      <text x="260" y="430" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="12" fill="white" font-weight="bold">
        🤖 Kod
      </text>
      <text x="260" y="450" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="10" fill="white">
        Generation
      </text>
      
      <!-- Modele -->
      <rect x="340" y="400" width="120" height="80" rx="10" fill="#764ba2" opacity="0.8">
        <animate attributeName="y" values="400;420;400" dur="2s" repeatCount="indefinite"/>
      </rect>
      <text x="400" y="430" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="12" fill="white" font-weight="bold">
        📦 Modele
      </text>
      <text x="400" y="450" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="10" fill="white">
        Management
      </text>
      
      <!-- Integracja -->
      <rect x="480" y="400" width="120" height="80" rx="10" fill="#667eea" opacity="0.8">
        <animate attributeName="y" values="420;400;420" dur="2s" begin="0.5s" repeatCount="indefinite"/>
      </rect>
      <text x="540" y="430" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="12" fill="white" font-weight="bold">
        🔗 HuggingFace
      </text>
      <text x="540" y="450" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="10" fill="white">
        Integration
      </text>
      
      <!-- Auto-install -->
      <rect x="620" y="400" width="120" height="80" rx="10" fill="#764ba2" opacity="0.8">
        <animate attributeName="y" values="400;420;400" dur="2s" begin="0.5s" repeatCount="indefinite"/>
      </rect>
      <text x="680" y="430" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="12" fill="white" font-weight="bold">
        ⚡ Auto
      </text>
      <text x="680" y="450" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="10" fill="white">
        Install
      </text>
      
      <!-- Interactive -->
      <rect x="760" y="400" width="120" height="80" rx="10" fill="#667eea" opacity="0.8">
        <animate attributeName="y" values="420;400;420" dur="2s" begin="1s" repeatCount="indefinite"/>
      </rect>
      <text x="820" y="430" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="12" fill="white" font-weight="bold">
        💬 Interactive
      </text>
      <text x="820" y="450" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="10" fill="white">
        CLI
      </text>
    </g>
    
    <!-- Badge PyLama -->
    <rect x="450" y="520" width="300" height="40" rx="20" fill="rgba(102, 126, 234, 0.2)" 
          stroke="#667eea" stroke-width="2" opacity="0">
      <animate attributeName="opacity" values="0;1" dur="1s" begin="4s" fill="freeze"/>
    </rect>
    <text x="600" y="545" text-anchor="middle" font-family="Arial, sans-serif" 
          font-size="16" fill="#667eea" font-weight="bold" opacity="0">
      🔗 Część ekosystemu PyLama
      <animate attributeName="opacity" values="0;1" dur="1s" begin="4s" fill="freeze"/>
    </text>
    
    <!-- Przejście do następnego slajdu -->
    <animateTransform attributeName="transform" type="translate" 
                      values="0,0; -1200,0" dur="1s" begin="8s" fill="freeze"/>
  </g>
  
  <!-- Slajd 2: Architektura -->
  <g id="slide2" transform="translate(1200,0)">
    <animateTransform attributeName="transform" type="translate" 
                      values="1200,0; 0,0" dur="1s" begin="8s" fill="freeze"/>
    
    <!-- Karta główna -->
    <rect x="100" y="80" width="1000" height="640" rx="20" fill="url(#cardGradient)" 
          filter="url(#shadow)" opacity="0">
      <animate attributeName="opacity" values="0;1" dur="1s" begin="9s" fill="freeze"/>
    </rect>
    
    <!-- Tytuł -->
    <text x="600" y="140" text-anchor="middle" font-family="Arial, sans-serif" 
          font-size="36" font-weight="bold" fill="url(#textGradient)" opacity="0">
      Architektura Systemu
      <animate attributeName="opacity" values="0;1" dur="1s" begin="9.5s" fill="freeze"/>
    </text>
    
    <!-- Diagram przepływu -->
    <g id="flow-diagram" opacity="0">
      <animate attributeName="opacity" values="0;1" dur="1s" begin="10s" fill="freeze"/>
      
      <!-- Użytkownik -->
      <rect x="520" y="180" width="160" height="60" rx="30" fill="#667eea" filter="url(#shadow)">
        <animate attributeName="fill" values="#667eea;#764ba2;#667eea" dur="3s" repeatCount="indefinite"/>
      </rect>
      <text x="600" y="210" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="16" fill="white" font-weight="bold">👤 Użytkownik</text>
      
      <!-- Strzałka 1 -->
      <path d="M 600 240 L 600 270" stroke="#667eea" stroke-width="3" marker-end="url(#arrowhead)">
        <animate attributeName="stroke-dasharray" values="0,30;30,0" dur="2s" repeatCount="indefinite"/>
      </path>
      
      <!-- CLI -->
      <rect x="520" y="280" width="160" height="60" rx="15" fill="#764ba2" filter="url(#shadow)">
        <animate attributeName="fill" values="#764ba2;#667eea;#764ba2" dur="3s" begin="0.5s" repeatCount="indefinite"/>
      </rect>
      <text x="600" y="310" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="16" fill="white" font-weight="bold">⚡ getllm CLI</text>
      
      <!-- Strzałka 2 -->
      <path d="M 600 340 L 600 370" stroke="#764ba2" stroke-width="3" marker-end="url(#arrowhead)">
        <animate attributeName="stroke-dasharray" values="0,30;30,0" dur="2s" begin="0.5s" repeatCount="indefinite"/>
      </path>
      
      <!-- Models.py -->
      <rect x="520" y="380" width="160" height="60" rx="15" fill="#667eea" filter="url(#shadow)">
        <animate attributeName="fill" values="#667eea;#764ba2;#667eea" dur="3s" begin="1s" repeatCount="indefinite"/>
      </rect>
      <text x="600" y="410" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="16" fill="white" font-weight="bold">🔧 models.py</text>
      
      <!-- Strzałka 3 -->
      <path d="M 600 440 L 600 470" stroke="#667eea" stroke-width="3" marker-end="url(#arrowhead)">
        <animate attributeName="stroke-dasharray" values="0,30;30,0" dur="2s" begin="1s" repeatCount="indefinite"/>
      </path>
      
      <!-- LogLama -->
      <rect x="520" y="480" width="160" height="60" rx="15" fill="#764ba2" filter="url(#shadow)">
        <animate attributeName="fill" values="#764ba2;#667eea;#764ba2" dur="3s" begin="1.5s" repeatCount="indefinite"/>
      </rect>
      <text x="600" y="510" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="16" fill="white" font-weight="bold">📝 LogLama</text>
      
      <!-- Strzałka 4 -->
      <path d="M 600 540 L 600 570" stroke="#764ba2" stroke-width="3" marker-end="url(#arrowhead)">
        <animate attributeName="stroke-dasharray" values="0,30;30,0" dur="2s" begin="1.5s" repeatCount="indefinite"/>
      </path>
      
      <!-- Ollama API -->
      <rect x="520" y="580" width="160" height="60" rx="15" fill="#667eea" filter="url(#shadow)">
        <animate attributeName="fill" values="#667eea;#764ba2;#667eea" dur="3s" begin="2s" repeatCount="indefinite"/>
      </rect>
      <text x="600" y="610" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="16" fill="white" font-weight="bold">🤖 Ollama API</text>
    </g>
    
    <!-- Kluczowe pliki po prawej -->
    <g id="key-files" opacity="0">
      <animate attributeName="opacity" values="0;1" dur="1s" begin="11s" fill="freeze"/>
      
      <text x="800" y="200" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#2d3748">
        Kluczowe Pliki:
      </text>
      
      <rect x="750" y="220" width="350" height="50" rx="10" fill="rgba(102, 126, 234, 0.1)" 
            stroke="#667eea" stroke-width="1">
        <animate attributeName="fill" values="rgba(102, 126, 234, 0.1);rgba(102, 126, 234, 0.2);rgba(102, 126, 234, 0.1)" 
                 dur="2s" repeatCount="indefinite"/>
      </rect>
      <text x="760" y="240" font-family="monospace" font-size="14" font-weight="bold" fill="#667eea">
        getllm/cli.py
      </text>
      <text x="760" y="255" font-family="Arial, sans-serif" font-size="12" fill="#718096">
        Główne CLI
      </text>
      
      <rect x="750" y="280" width="350" height="50" rx="10" fill="rgba(118, 75, 162, 0.1)" 
            stroke="#764ba2" stroke-width="1">
        <animate attributeName="fill" values="rgba(118, 75, 162, 0.1);rgba(118, 75, 162, 0.2);rgba(118, 75, 162, 0.1)" 
                 dur="2s" begin="0.5s" repeatCount="indefinite"/>
      </rect>
      <text x="760" y="300" font-family="monospace" font-size="14" font-weight="bold" fill="#764ba2">
        getllm/interactive_cli.py
      </text>
      <text x="760" y="315" font-family="Arial, sans-serif" font-size="12" fill="#718096">
        Interaktywna powłoka
      </text>
      
      <rect x="750" y="340" width="350" height="50" rx="10" fill="rgba(102, 126, 234, 0.1)" 
            stroke="#667eea" stroke-width="1">
        <animate attributeName="fill" values="rgba(102, 126, 234, 0.1);rgba(102, 126, 234, 0.2);rgba(102, 126, 234, 0.1)" 
                 dur="2s" begin="1s" repeatCount="indefinite"/>
      </rect>
      <text x="760" y="360" font-family="monospace" font-size="14" font-weight="bold" fill="#667eea">
        getllm/models.py
      </text>
      <text x="760" y="375" font-family="Arial, sans-serif" font-size="12" fill="#718096">
        Logika modeli, integracja Ollama
      </text>
      
      <rect x="750" y="400" width="350" height="50" rx="10" fill="rgba(118, 75, 162, 0.1)" 
            stroke="#764ba2" stroke-width="1">
        <animate attributeName="fill" values="rgba(118, 75, 162, 0.1);rgba(118, 75, 162, 0.2);rgba(118, 75, 162, 0.1)" 
                 dur="2s" begin="1.5s" repeatCount="indefinite"/>
      </rect>
      <text x="760" y="420" font-family="monospace" font-size="14" font-weight="bold" fill="#764ba2">
        .env/env.example
      </text>
      <text x="760" y="435" font-family="Arial, sans-serif" font-size="12" fill="#718096">
        Konfiguracja środowiska
      </text>
    </g>
    
    <!-- Przejście do następnego slajdu -->
    <animateTransform attributeName="transform" type="translate" 
                      values="0,0; -1200,0" dur="1s" begin="16s" fill="freeze"/>
  </g>
  
  <!-- Slajd 3: Przykłady użycia -->
  <g id="slide3" transform="translate(1200,0)">
    <animateTransform attributeName="transform" type="translate" 
                      values="1200,0; 0,0" dur="1s" begin="16s" fill="freeze"/>
    
    <!-- Karta główna -->
    <rect x="100" y="80" width="1000" height="640" rx="20" fill="url(#cardGradient)" 
          filter="url(#shadow)" opacity="0">
      <animate attributeName="opacity" values="0;1" dur="1s" begin="17s" fill="freeze"/>
    </rect>
    
    <!-- Tytuł -->
    <text x="600" y="140" text-anchor="middle" font-family="Arial, sans-serif" 
          font-size="36" font-weight="bold" fill="url(#textGradient)" opacity="0">
      Przykłady Użycia
      <animate attributeName="opacity" values="0;1" dur="1s" begin="17.5s" fill="freeze"/>
    </text>
    
    <!-- Terminal okno -->
    <g id="terminal" opacity="0">
      <animate attributeName="opacity" values="0;1" dur="1s" begin="18s" fill="freeze"/>
      
      <!-- Nagłówek terminala -->
      <rect x="150" y="180" width="900" height="40" rx="10" fill="#2d3748"/>
      <circle cx="170" cy="200" r="6" fill="#ff5f56"/>
      <circle cx="190" cy="200" r="6" fill="#ffbd2e"/>
      <circle cx="210" cy="200" r="6" fill="#27ca3f"/>
      <text x="250" y="205" font-family="Arial, sans-serif" font-size="14" fill="#a0aec0">
        Terminal - getllm
      </text>
      
      <!-- Zawartość terminala -->
      <rect x="150" y="220" width="900" height="400" fill="#1a202c"/>
      
      <!-- Komendy z animacją pisania -->
      <text x="170" y="250" font-family="monospace" font-size="14" fill="#68d391">
        $ 
        <tspan fill="#e2e8f0" opacity="0">getllm "stwórz funkcję fibonacci"
          <animate attributeName="opacity" values="0;1" dur="0.1s" begin="18.5s" fill="freeze"/>
        </tspan>
      </text>
      
      <text x="170" y="280" font-family="monospace" font-size="12" fill="#a0aec0" opacity="0">
        Generowanie kodu z modelem codellama:7b...
        <animate attributeName="opacity" values="0;1" dur="0.5s" begin="19s" fill="freeze"/>
      </text>
      
      <text x="170" y="310" font-family="monospace" font-size="12" fill="#68d391" opacity="0">
        ✓ Kod wygenerowany pomyślnie!
        <animate attributeName="opacity" values="0;1" dur="0.5s" begin="19.5s" fill="freeze"/>
      </text>
      
      <text x="170" y="350" font-family="monospace" font-size="14" fill="#68d391" opacity="0">
        $ 
        <tspan fill="#e2e8f0">getllm -r "serwer Flask"</tspan>
        <animate attributeName="opacity" values="0;1" dur="0.1s" begin="20s" fill="freeze"/>
      </text>
      
      <text x="170" y="380" font-family="monospace" font-size="12" fill="#a0aec0" opacity="0">
        Generowanie i uruchamianie kodu...
        <animate attributeName="opacity" values="0;1" dur="0.5s" begin="20.5s" fill="freeze"/>
      </text>
      
      <text x="170" y="410" font-family="monospace" font-size="12" fill="#68d391" opacity="0">
        ✓ Serwer uruchomiony na porcie 5000
        <animate attributeName="opacity" values="0;1" dur="0.5s" begin="21s" fill="freeze"/>
      </text>
      
      <text x="170" y="450" font-family="monospace" font-size="14" fill="#68d391" opacity="0">
        $ 
        <tspan fill="#e2e8f0">getllm list</tspan>
        <animate attributeName="opacity" values="0;1" dur="0.1s" begin="21.5s" fill="freeze"/>
      </text>
      
      <text x="170" y="480" font-family="monospace" font-size="12" fill="#e2e8f0" opacity="0">
        📦 codellama:7b - Dostępny
        <animate attributeName="opacity" values="0;1" dur="0.5s" begin="22s" fill="freeze"/>
      </text>
      
      <text x="170" y="500" font-family="monospace" font-size="12" fill="#e2e8f0" opacity="0">
        📦 phi3:latest - Dostępny  
        <animate attributeName="opacity" values="0;1" dur="0.5s" begin="22.2s" fill="freeze"/>
      </text>
      
      <text x="170" y="520" font-family="monospace" font-size="12" fill="#e2e8f0" opacity="0">
        📦 deepseek-coder:6.7b - Zainstalowany
        <animate attributeName="opacity" values="0;1" dur="0.5s" begin="22.4s" fill="freeze"/>
      </text>
      
      <!-- Kursor migający -->
      <text x="170" y="550" font-family="monospace" font-size="14" fill="#68d391" opacity="0">
        $ 
        <tspan fill="#e2e8f0">█</tspan>
        <animate attributeName="opacity" values="0;1" dur="0.1s" begin="23s" fill="freeze"/>
        <animate attributeName="opacity" values="1;0;1" dur="1s" begin="23s" repeatCount="indefinite"/>
      </text>
    </g>
    
    <!-- Funkcje po prawej -->
    <g id="features-list" opacity="0">
      <animate attributeName="opacity" values="0;1" dur="1s" begin="18.5s" fill="freeze"/>
      
      <text x="150" y="660" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#2d3748">
        🚀 Kluczowe Funkcje:
      </text>
      
      <text x="170" y="685" font-family="Arial, sans-serif" font-size="14" fill="#4a5568">
        • Automatyczna instalacja modeli
      </text>
      <text x="170" y="705" font-family="Arial, sans-serif" font-size="14" fill="#4a5568">
        • Tryb interaktywny z menu
      </text>
      <text x="500" y="685" font-family="Arial, sans-serif" font-size="14" fill="#4a5568">
        • Integracja z HuggingFace
      </text>
      <text x="500" y="705" font-family="Arial, sans-serif" font-size="14" fill="#4a5568">
        • Mechanizmy fallback
      </text>
      <text x="800" y="685" font-family="Arial, sans-serif" font-size="14" fill="#4a5568">
        • Wykonywanie kodu
      </text>
      <text x="800" y="705" font-family="Arial, sans-serif" font-size="14" fill="#4a5568">
        • Centralne logowanie
      </text>
    </g>
    
    <!-- Przejście do kolejnego slajdu po czasie -->
    <animateTransform attributeName="transform" type="translate" 
                      values="0,0; -1200,0" dur="1s" begin="24s" fill="freeze"/>
  </g>
  
  <!-- Slajd 4: Zakończenie -->
  <g id="slide4" transform="translate(1200,0)">
    <animateTransform attributeName="transform" type="translate" 
                      values="1200,0; 0,0" dur="1s" begin="24s" fill="freeze"/>
    
    <!-- Karta główna z gradientem -->
    <rect x="100" y="100" width="1000" height="600" rx="20" fill="url(#bgGradient)" 
          filter="url(#shadow)" opacity="0">
      <animate attributeName="opacity" values="0;1" dur="1s" begin="25s" fill="freeze"/>
    </rect>
    
    <!-- Dziękujemy -->
    <text x="600" y="250" text-anchor="middle" font-family="Arial, sans-serif" 
          font-size="48" font-weight="bold" fill="white" filter="url(#glow)" opacity="0">
      Dziękujemy za uwagę!
      <animate attributeName="opacity" values="0;1" dur="1s" begin="25.5s" fill="freeze"/>
      <animateTransform attributeName="transform" type="scale" 
                        values="0.8;1.1;1" dur="1s" begin="25.5s" fill="freeze"/>
    </text>
    
    <!-- Logo ponownie -->
    <text x="600" y="350" text-anchor="middle" font-family="Arial, sans-serif" 
          font-size="64" font-weight="bold" fill="white" filter="url(#glow)" opacity="0">
      getllm
      <animate attributeName="opacity" values="0;1" dur="1s" begin="26s" fill="freeze"/>
      <animate attributeName="font-size" values="64;72;64" dur="2s" begin="26s" repeatCount="indefinite"/>
    </text>
    
    <!-- Opis końcowy -->
    <text x="600" y="420" text-anchor="middle" font-family="Arial, sans-serif" 
          font-size="24" fill="rgba(255,255,255,0.9)" opacity="0">
      Twój wszechstronny pomocnik w zarządzaniu modelami AI
      <animate attributeName="opacity" values="0;1" dur="1s" begin="26.5s" fill="freeze"/>
    </text>
    
    <!-- Ikony końcowe -->
    <g id="final-icons" opacity="0">
      <animate attributeName="opacity" values="0;1" dur="1s" begin="27s" fill="freeze"/>
      
      <text x="400" y="500" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="18" fill="white">
        🔗 PyLama
      </text>
      <text x="600" y="500" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="18" fill="white">
        🤖 Ollama
      </text>
      <text x="800" y="500" text-anchor="middle" font-family="Arial, sans-serif" 
            font-size="18" fill="white">
        ⚡ Auto-install
      </text>
    </g>
    
    <!-- Efekt fajerwerków -->
    <g id="fireworks">
      <circle r="3" fill="yellow" opacity="0">
        <animate attributeName="r" values="0;20;0" dur="2s" begin="28s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;1;0" dur="2s" begin="28s" repeatCount="indefinite"/>
        <animateMotion dur="2s" begin="28s" repeatCount="indefinite" 
                       path="M 300,600 Q 400,200 500,600"/>
      </circle>
      <circle r="3" fill="cyan" opacity="0">
        <animate attributeName="r" values="0;15;0" dur="1.5s" begin="28.5s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;1;0" dur="1.5s" begin="28.5s" repeatCount="indefinite"/>
        <animateMotion dur="1.5s" begin="28.5s" repeatCount="indefinite" 
                       path="M 700,600 Q 600,250 900,600"/>
      </circle>
      <circle r="3" fill="magenta" opacity="0">
        <animate attributeName="r" values="0;25;0" dur="3s" begin="29s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;1;0" dur="3s" begin="29s" repeatCount="indefinite"/>
        <animateMotion dur="3s" begin="29s" repeatCount="indefinite" 
                       path="M 600,600 Q 700,150 400,600"/>
      </circle>
    </g>
  </g>
  
  <!-- Definicje markerów dla strzałek -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" 
            refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#667eea"/>
    </marker>
  </defs>
  
  <!-- Sterowanie prezentacją -->
  <g id="controls" opacity="0.7">
    <rect x="50" y="750" width="100" height="30" rx="15" fill="#667eea" 
          stroke="white" stroke-width="1"/>
    <text x="100" y="770" text-anchor="middle" font-family="Arial, sans-serif" 
          font-size="12" fill="white" font-weight="bold">
      Auto Play
    </text>
  </g>
  
  <!-- Wskaźnik postępu -->
  <rect x="200" y="760" width="800" height="6" rx="3" fill="rgba(255,255,255,0.3)"/>
  <rect x="200" y="760" width="0" height="6" rx="3" fill="white">
    <animate attributeName="width" values="0;200;400;600;800" 
             dur="32s" fill="freeze"/>
  </rect>
</svg>

## Features

- **Code Generation**: Generate Python code using LLM models
- **Model Management**: Install, list, and select models
- **Hugging Face Integration**: Search and install models from Hugging Face
- **Automatic Model Installation**: Automatically install models when they are not found
- **Fallback Mechanisms**: Use fallback models when the requested model is not available
- **Environment Configuration**: Configure Ollama through environment variables
- **Special Model Handling**: Special installation process for SpeakLeash Bielik models
- **Mock Mode**: Support for mock mode without requiring Ollama
- **Interactive Mode**: Interactive CLI for model selection and code generation
- **Template System**: Generate code with awareness of platform, dependencies, and more
- **Code Execution**: Execute generated code directly

## LogLama Integration

PyLLM integrates with LogLama as the primary service in the PyLama ecosystem. This integration provides:

- **Centralized Environment Management**: Environment variables are loaded from the central `.env` file in the `devlama` directory
- **Shared Configuration**: Model configurations are shared across all PyLama components
- **Dependency Management**: Dependencies are validated and installed by LogLama
- **Service Orchestration**: Services are started in the correct order using LogLama CLI
- **Centralized Logging**: All PyLLM operations are logged to the central LogLama system
- **Structured Logging**: Logs include component context for better filtering and analysis
- **Health Monitoring**: LogLama monitors PyLLM service health and availability

---

## General Diagram (Mermaid)
```mermaid
graph TD
    A[User] -->|CLI/Interactive| B[getllm/cli.py]
    B --> C[models.py]
    B --> D[interactive_cli.py]
    C --> E[LogLama Central .env]
    C --> F[Ollama API]
    D --> B
    G[LogLama] --> E
```

---

## ASCII Diagram: CLI Command Flow
```
User
    |
    v
+-----------------+
|   getllm CLI     |
+-----------------+
    |
    v
+-----------------+
|   models.py     |
+-----------------+
    |
+-----------------+
| LogLama Central |
|    .env File    |
+-----------------+
    |
+-----------------+
|  Ollama API     |
+-----------------+
```

---

## Usage

### Basic Usage

```bash
# Start interactive mode
getllm -i

# List available models
getllm list

# Install a model
getllm install codellama:7b

# Set default model
getllm set-default codellama:7b

# Search for models on Hugging Face
getllm --search bielik

# Update models list from Hugging Face
getllm --update-hf
```

> **Note**: Direct code generation with `getllm "prompt"` is currently being migrated from the `devlama` package. Use the interactive mode (`getllm -i`) for code generation in the meantime.

### Model Management

```bash
# List available models
getllm list

# Install a model
getllm install codellama:7b

# List installed models
getllm installed

# Set default model
getllm set-default codellama:7b

# Show default model
getllm default

# Update models list from Ollama
getllm update
```

### Hugging Face Integration

The Hugging Face integration allows you to search for and install models directly from Hugging Face:

```bash
# Search for models on Hugging Face
getllm --search bielik

# Update models list from Hugging Face
getllm --update-hf
```

## Known Issues

- **Direct Code Generation**: The direct code generation functionality (e.g., `getllm "create a function"`) is currently being migrated from the `devlama` package. Use the interactive mode (`getllm -i`) for code generation in the meantime.

- **Error Message**: If you try to use direct code generation, you might see an error like `AttributeError: 'OllamaIntegration' object has no attribute 'query_ollama'`. This will be fixed in an upcoming update.

### Interactive Mode

```bash
# Start interactive mode
getllm -i

# Start interactive mode with mock implementation
getllm -i --mock
```

---

## Installation

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .  # This is important! Always install in development mode before starting
```

> **IMPORTANT**: Always run `pip install -e .` before starting the project to ensure all dependencies are properly installed and the package is available in development mode.

---

## Using the Makefile

PyLLM includes a Makefile to simplify common development tasks:

```bash
# Set up the project (creates a virtual environment and installs dependencies)
make setup

# Run the API server (default port 8001)
make run

# Run the API server on a custom port
make run PORT=8080

# The run-port command is also available for backward compatibility
make run-port PORT=8080

# Run tests
make test

# Format code with black
make format

# Lint code with flake8
make lint

# Clean up project (remove __pycache__, etc.)
make clean

# Show all available commands
make help
```

---

## Key Files

- `getllm/cli.py` – main CLI
- `getllm/interactive_cli.py` – interactive shell with menu and cursor selection
- `getllm/models.py` – model logic, .env/env.example handling, Ollama integration
- `.env`/`env.example` – environment config and default model

---

## Example Usage

Search polish moel bielik in huggingface
```bash
getllm --search bielik
```
from huggingface 

```bash
Searching for models matching 'bielik' on Hugging Face...
Searching for models matching 'bielik' on Hugging Face...
? Select a model to install: (Use arrow keys)
 » speakleash/Bielik-11B-v2.3-Instruct-FP8            Unknown    Downloads: 26,103 |
   speakleash/Bielik-11B-v2.3-Instruct-GGUF           Unknown    Downloads: 2,203 |
   speakleash/Bielik-4.5B-v3.0-Instruct-GGUF          Unknown    Downloads: 967 |
   speakleash/Bielik-7B-Instruct-v0.1-GGUF            Unknown    Downloads: 712 |
   speakleash/Bielik-1.5B-v3.0-Instruct-GGUF          Unknown    Downloads: 423 |
   bartowski/Bielik-11B-v2.2-Instruct-GGUF            Unknown    Downloads: 382 |
   gaianet/Bielik-4.5B-v3.0-Instruct-GGUF             Unknown    Downloads: 338 |
   second-state/Bielik-1.5B-v3.0-Instruct-GGUF        Unknown    Downloads: 314 |
   second-state/Bielik-4.5B-v3.0-Instruct-GGUF        Unknown    Downloads: 306 |
   DevQuasar/speakleash.Bielik-4.5B-v3.0-Instruct-GGUF Unknown    Downloads: 219 |
   DevQuasar/speakleash.Bielik-1.5B-v3.0-Instruct-GGUF Unknown    Downloads: 219 |
   gaianet/Bielik-11B-v2.3-Instruct-GGUF              Unknown    Downloads: 173 |
   tensorblock/Bielik-11B-v2.2-Instruct-GGUF          Unknown    Downloads: 168 |
   speakleash/Bielik-11B-v2.2-Instruct-GGUF           Unknown    Downloads: 162 |
   mradermacher/Bielik-11B-v2-i1-GGUF                 Unknown    Downloads: 147 |
   gaianet/Bielik-1.5B-v3.0-Instruct-GGUF             Unknown    Downloads: 145 |
   QuantFactory/Bielik-7B-v0.1-GGUF                   Unknown    Downloads: 135 |
   second-state/Bielik-11B-v2.3-Instruct-GGUF         Unknown    Downloads: 125 |
   RichardErkhov/speakleash_-_Bielik-11B-v2.1-Instruct-gguf Unknown    Downloads: 113 |
   mradermacher/Bielik-7B-v0.1-GGUF                   Unknown    Downloads: 94 |
   Cancel
```

on local environment
```bash
Searching for models matching 'bielik' on Hugging Face...
Searching for models matching 'bielik' on Hugging Face...
? Select a model to install: speakleash/Bielik-1.5B-v3.0-Instruct-GGUF          Unknown    Downloads: 423 | 
? Do you want to install this model now? Yes

Detected SpeakLeash Bielik model: speakleash/Bielik-1.5B-v3.0-Instruct-GGUF
Starting special installation process...

Found existing Bielik model installation: bielik-custom-1747866289:latest
Using existing model instead of downloading again.
Increased API timeout to 120 seconds for Bielik model.
Updated .env file with model settings: ~/getllm/.env
```    

### List available models
```bash
getllm list
```

### Install a model
```bash
getllm install deepseek-coder:6.7b
```

### Set default model
```bash
getllm set-default deepseek-coder:6.7b
```

### Show default model
```bash
getllm default
```

### Update model list from Ollama
```bash
getllm update
```

### Run interactive mode (menu, cursor selection)
```bash
getllm -i
```

---

## set_default_model function flow (Mermaid)
```mermaid
flowchart TD
    S[Start] --> C{Does .env exist?}
    C -- Yes --> R[Update OLLAMA_MODEL in .env]
    C -- No --> K[Copy env.example to .env]
    K --> R
    R --> E[End]
```

---

## Interactive mode - menu (ASCII)
```
+--------------------------------+
|  getllm - interactive mode       |
+--------------------------------+
| > List available models         |
|   Show default model           |
|   List installed models        |
|   Install model                |
|   Set default model            |
|   Update model list            |
|   Test default model           |
|   Exit                         |
+--------------------------------+
  (navigation: arrow keys + Enter)
```

---

## Installation

```bash
pip install getllm
```

## Usage

### Basic Model Management

```python
from getllm import get_models, get_default_model, set_default_model, install_model

# Get available models
models = get_models()
for model in models:
    print(f"{model['name']} - {model.get('desc', '')}")

# Get the current default model
default_model = get_default_model()
print(f"Current default model: {default_model}")

# Set a new default model
set_default_model("codellama:7b")

# Install a model
install_model("deepseek-coder:6.7b")
```

### Direct Ollama Integration

```python
from getllm import OllamaIntegration, get_ollama_integration, start_ollama_server

# Start the Ollama server if it's not already running
ollama = start_ollama_server()

# Or create an OllamaIntegration instance with a specific model
ollama = get_ollama_integration(model="codellama:7b")

# Check if the model is available
if ollama.check_model_availability():
    print(f"Model {ollama.model} is available")
else:
    print(f"Model {ollama.model} is not available")

    # Install the model
    if ollama.install_model(ollama.model):
        print(f"Successfully installed {ollama.model}")

# List installed models
installed_models = ollama.list_installed_models()
for model in installed_models:
    print(f"Installed model: {model['name']}")
```

## Environment Variables

The package uses the following environment variables for Ollama integration:

- `OLLAMA_PATH`: Path to the Ollama executable (default: 'ollama')
- `OLLAMA_MODEL`: Default model to use (default: 'codellama:7b')
- `OLLAMA_FALLBACK_MODELS`: Comma-separated list of fallback models (default: 'codellama:7b,phi3:latest,tinyllama:latest')
- `OLLAMA_AUTO_SELECT_MODEL`: Whether to automatically select an available model if the requested model is not found (default: 'true')
- `OLLAMA_AUTO_INSTALL_MODEL`: Whether to automatically install a model when it's not found (default: 'true')
- `OLLAMA_TIMEOUT`: API timeout in seconds (default: '30')

These variables can be set in a .env file in the project root directory or in the system environment.

## License
This project is licensed under the Apache 2.0 License (see LICENSE file).
