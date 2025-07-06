// Открытие/закрытие модального окна инвестиционного калькулятора
function openInvestCalcModal() {
  document.getElementById('invest-calc-modal').classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}
function closeInvestCalcModal() {
  document.getElementById('invest-calc-modal').classList.add('hidden');
  document.body.style.overflow = '';
}
// Закрытие по ESC и клику вне окна
window.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeInvestCalcModal();
});
document.addEventListener('click', function(e) {
  const modal = document.getElementById('invest-calc-modal');
  if (modal && !modal.classList.contains('hidden') && e.target === modal) {
    closeInvestCalcModal();
  }
}); 