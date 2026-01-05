/**
 * 生徒ホーム画面のJavaScript
 * カレンダー表示とタスク管理機能を提供
 */

document.addEventListener('DOMContentLoaded', function() {
    // カレンダー機能の初期化
    initCalendar();
    
    // タスク機能の初期化
    initTasks();
});

/**
 * カレンダー機能の初期化
 */
function initCalendar() {
    const calendarBody = document.getElementById('calendarBody');
    const currentMonthElement = document.getElementById('currentMonth');
    const prevMonthBtn = document.getElementById('prevMonth');
    const nextMonthBtn = document.getElementById('nextMonth');
    
    if (!calendarBody || !currentMonthElement) {
        console.warn('Calendar elements not found');
        return;
    }
    
    let currentDate = new Date();
    
    /**
     * カレンダーを描画
     */
    function renderCalendar() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        
        // 月表示を更新
        currentMonthElement.textContent = `${month + 1}月`;
        
        // 月の最初の日と最後の日を取得
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        
        // カレンダーの開始日（前月の日付を含む）
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay());
        
        // カレンダーをクリア
        calendarBody.innerHTML = '';
        
        // 6週間分の日付を表示（42日）
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        for (let i = 0; i < 42; i++) {
            const date = new Date(startDate);
            date.setDate(date.getDate() + i);
            
            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day';
            
            // 他の月の日付
            if (date.getMonth() !== month) {
                dayElement.classList.add('other-month');
            }
            
            // 今日の日付
            if (date.getTime() === today.getTime()) {
                dayElement.classList.add('today');
            }
            
            // 日付番号
            const dayNumber = document.createElement('div');
            dayNumber.className = 'day-number';
            dayNumber.textContent = date.getDate();
            dayElement.appendChild(dayNumber);
            
            // イベントインジケーター（デモ用）
            // 実際のデータがある場合はここに表示
            const eventsContainer = document.createElement('div');
            eventsContainer.className = 'day-events';
            dayElement.appendChild(eventsContainer);
            
            // クリックイベント
            dayElement.addEventListener('click', function() {
                handleDayClick(date);
            });
            
            calendarBody.appendChild(dayElement);
        }
    }
    
    /**
     * 日付クリック時の処理
     */
    function handleDayClick(date) {
        console.log('Clicked date:', date);
        // ここに日付クリック時の処理を追加
        // 例: その日のタスクをフィルタリング、詳細表示など
    }
    
    /**
     * 前月へ移動
     */
    function previousMonth() {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    }
    
    /**
     * 次月へ移動
     */
    function nextMonth() {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    }
    
    // イベントリスナーを設定
    if (prevMonthBtn) {
        prevMonthBtn.addEventListener('click', previousMonth);
    }
    
    if (nextMonthBtn) {
        nextMonthBtn.addEventListener('click', nextMonth);
    }
    
    // 初期表示
    renderCalendar();
}

/**
 * タスク機能の初期化
 */
function initTasks() {
    const taskCheckboxes = document.querySelectorAll('.task-checkbox');
    
    taskCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('click', function(e) {
            e.preventDefault();
            handleTaskComplete(this);
        });
    });
}

/**
 * タスク完了処理
 */
function handleTaskComplete(checkboxElement) {
    const taskCard = checkboxElement.closest('.task-card');
    const taskId = checkboxElement.dataset.taskId;
    
    if (!taskCard) {
        return;
    }
    
    // タスク完了状態をトグル
    taskCard.classList.toggle('completed');
    
    // サーバーにタスク完了状態を送信
    if (taskId) {
        updateTaskStatus(taskId, taskCard.classList.contains('completed'));
    }
    
    // タスクカウントを更新
    updateTaskCount();
}

/**
 * タスク状態をサーバーに送信
 */
function updateTaskStatus(taskId, isCompleted) {
    // CSRFトークンを取得
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/api/tasks/${taskId}/complete/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            completed: isCompleted
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Task updated:', data);
    })
    .catch(error => {
        console.error('Error updating task:', error);
    });
}

/**
 * タスクカウントを更新
 */
function updateTaskCount() {
    const taskCards = document.querySelectorAll('.task-card:not(.completed)');
    const countElement = document.querySelector('.count-number');
    
    if (countElement) {
        countElement.textContent = taskCards.length;
    }
}

/**
 * Cookieから値を取得
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * チェックインボタンの処理
 */
const checkinBtn = document.querySelector('.checkin-btn');
if (checkinBtn) {
    checkinBtn.addEventListener('click', function() {
        handleCheckin();
    });
}

/**
 * チェックイン処理
 */
function handleCheckin() {
    const csrftoken = getCookie('csrftoken');
    
    fetch('/api/checkin/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Checked in:', data);
        // チェックイン成功時の処理
        // 例: ログイン日数を更新、アニメーション表示など
        showCheckinSuccess();
    })
    .catch(error => {
        console.error('Error checking in:', error);
    });
}

/**
 * チェックイン成功メッセージを表示
 */
function showCheckinSuccess() {
    // TODO: トースト通知やアニメーションを実装
    alert('チェックイン完了！');
}
