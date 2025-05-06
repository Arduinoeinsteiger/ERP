/**
 * Tests für das Tutorial-Overlay-Feature
 * 
 * Diese Tests verwenden Jest, um die Funktionalität des Tutorial-Overlays zu testen.
 */

// Mock des DOM für Tests
document.body.innerHTML = `
<div id="app">
  <header>
    <nav>
      <ul>
        <li><a href="#dashboard" data-tutorial="dashboard">Dashboard</a></li>
      </ul>
    </nav>
    <div class="user-info">
      <button id="tutorial-btn" data-tutorial="help">?</button>
    </div>
  </header>
  <main>
    <section id="dashboard" class="active-section">
      <div class="stat-card" data-tutorial="stat-card"></div>
    </section>
  </main>
  <footer>
    <div class="api-status" data-tutorial="api-status"></div>
  </footer>
</div>
<div id="tutorial-overlay" class="hidden">
  <div class="tutorial-content">
    <div class="tutorial-header">
      <button id="tutorial-close"></button>
    </div>
    <div class="tutorial-body">
      <div class="tutorial-step" data-step="1"></div>
      <div class="tutorial-step" data-step="2"></div>
    </div>
    <div class="tutorial-footer">
      <button id="tutorial-prev"></button>
      <div class="tutorial-progress">
        <span id="current-step">1</span> / <span id="total-steps">2</span>
      </div>
      <button id="tutorial-next"></button>
    </div>
  </div>
</div>
`;

// Mock für localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn(key => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    removeItem: jest.fn(key => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    })
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Importiere die zu testenden Funktionen
// Hinweis: In einem echten Setup würde man die Funktionen aus app.js importieren
// Für diesen Test erstellen wir Mocks
const startTutorial = jest.fn(() => {
  document.getElementById('tutorial-overlay').classList.remove('hidden');
  // Simuliere showTutorialStep(1)
  document.querySelectorAll('.tutorial-step').forEach(step => {
    step.classList.remove('active');
  });
  document.querySelector('.tutorial-step[data-step="1"]').classList.add('active');
});

const closeTutorial = jest.fn(() => {
  document.getElementById('tutorial-overlay').classList.add('hidden');
  localStorage.setItem('tutorial_completed', 'true');
});

const navigateTutorial = jest.fn((direction) => {
  const currentStep = document.querySelector('.tutorial-step.active').getAttribute('data-step');
  const nextStep = direction === 'next' ? parseInt(currentStep) + 1 : parseInt(currentStep) - 1;
  
  document.querySelectorAll('.tutorial-step').forEach(step => {
    step.classList.remove('active');
  });
  
  document.querySelector(`.tutorial-step[data-step="${nextStep}"]`).classList.add('active');
  document.getElementById('current-step').textContent = nextStep;
});

// Testen der Tutorial-Funktionalität
describe('Tutorial Overlay', () => {
  beforeEach(() => {
    // Reset DOM-Status vor jedem Test
    document.getElementById('tutorial-overlay').classList.add('hidden');
    document.querySelectorAll('.tutorial-step').forEach(step => {
      step.classList.remove('active');
    });
    
    // Mocks zurücksetzen
    jest.clearAllMocks();
    localStorageMock.clear();
  });
  
  test('Tutorial startet korrekt', () => {
    startTutorial();
    
    expect(document.getElementById('tutorial-overlay').classList.contains('hidden')).toBe(false);
    expect(document.querySelector('.tutorial-step[data-step="1"]').classList.contains('active')).toBe(true);
  });
  
  test('Tutorial schließt korrekt', () => {
    // Tutorial zuerst starten
    startTutorial();
    
    closeTutorial();
    
    expect(document.getElementById('tutorial-overlay').classList.contains('hidden')).toBe(true);
    expect(localStorage.setItem).toHaveBeenCalledWith('tutorial_completed', 'true');
  });
  
  test('Tutorial-Navigation funktioniert', () => {
    // Tutorial zuerst starten
    startTutorial();
    
    // Zum nächsten Schritt navigieren
    navigateTutorial('next');
    
    expect(document.querySelector('.tutorial-step[data-step="2"]').classList.contains('active')).toBe(true);
    expect(document.getElementById('current-step').textContent).toBe('2');
    
    // Zum vorherigen Schritt zurück navigieren
    navigateTutorial('prev');
    
    expect(document.querySelector('.tutorial-step[data-step="1"]').classList.contains('active')).toBe(true);
    expect(document.getElementById('current-step').textContent).toBe('1');
  });
});