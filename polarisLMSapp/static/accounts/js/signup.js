/**
 * サインアップページのJavaScript
 * ユーザータイプに応じて学年フィールドの表示/非表示を制御
 */

document.addEventListener('DOMContentLoaded', function() {
    const userTypeField = document.getElementById('id_user_type');
    const gradeField = document.getElementById('grade-field');
    
    if (!userTypeField || !gradeField) {
        console.error('Required elements not found');
        return;
    }
    
    /**
     * 学年フィールドの表示/非表示を切り替え
     */
    function toggleGradeField() {
        if (userTypeField.value === 'student') {
            gradeField.classList.add('show');
        } else {
            gradeField.classList.remove('show');
            // 生徒以外が選択された場合は学年フィールドをクリア
            const gradeInput = document.getElementById('id_grade');
            if (gradeInput) {
                gradeInput.value = '';
            }
        }
    }
    
    // 初期表示（エラー時などに生徒が選択されている場合に対応）
    toggleGradeField();
    
    // user_type変更時のイベントリスナー
    userTypeField.addEventListener('change', toggleGradeField);
});
