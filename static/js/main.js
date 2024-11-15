function getMoscowDate() {
        const now = new Date();
        const moscowOffset = 3 * 60;
        const localOffset = now.getTimezoneOffset();
        const moscowTime = new Date(now.getTime() + (moscowOffset - localOffset) * 60 * 1000);
        return new Date(moscowTime.getFullYear(), moscowTime.getMonth(), moscowTime.getDate());
    }

    const moscowDate = getMoscowDate();
    const formattedMoscowDate = moscowDate.toISOString().split('T')[0];

    const checkInInput = document.getElementById('luxCheckIn');
    const checkOutInput = document.getElementById('luxCheckOut');

    checkInInput.min = formattedMoscowDate;

    checkInInput.addEventListener('change', function () {
        checkOutInput.min = this.value;
    });

    if (checkInInput.value) {
        checkOutInput.min = checkInInput.value;
    }