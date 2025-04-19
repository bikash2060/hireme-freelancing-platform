document.addEventListener('DOMContentLoaded', function () {
    const illustrationControls = document.querySelectorAll('.control-dot');
    const illustrationItems = document.querySelectorAll('.illustration-item');

    illustrationControls.forEach(dot => {
        dot.addEventListener('click', function () {
            const step = this.getAttribute('data-step');

            illustrationControls.forEach(d => d.classList.remove('active'));
            illustrationItems.forEach(item => item.classList.remove('active'));

            this.classList.add('active');
            document.querySelector(`.illustration-item:nth-child(${step})`).classList.add('active');
        });
    });

    let currentStep = 1;
    const totalSteps = illustrationControls.length;

    function rotateIllustration() {
        illustrationControls.forEach(d => d.classList.remove('active'));
        illustrationItems.forEach(item => item.classList.remove('active'));

        document.querySelector(`.control-dot[data-step="${currentStep}"]`).classList.add('active');
        document.querySelector(`.illustration-item:nth-child(${currentStep})`).classList.add('active');

        currentStep = currentStep >= totalSteps ? 1 : currentStep + 1;
    }

    if (illustrationItems.length > 0) {
        setInterval(rotateIllustration, 4000);
    }
});
