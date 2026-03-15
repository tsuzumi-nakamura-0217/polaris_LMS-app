document.addEventListener('DOMContentLoaded', function () {
    const typeSelect = document.getElementById('id_problem_type');
    const choiceSection = document.getElementById('choice-section');

    if (!typeSelect || !choiceSection) {
        return;
    }

    function toggleChoices() {
        if (typeSelect.value === 'choice') {
            choiceSection.style.display = 'block';
        } else {
            choiceSection.style.display = 'none';
        }
    }

    typeSelect.addEventListener('change', toggleChoices);
    toggleChoices();
});