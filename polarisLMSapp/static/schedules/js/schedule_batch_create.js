document.addEventListener('DOMContentLoaded', function() {
    const subjectSelect = document.getElementById('subject_id');
    const gradeSelect = document.getElementById('grade');
    const categorySelect = document.getElementById('category_id');
    const categoryOverlay = document.getElementById('category_overlay');
    const categoryWarning = document.getElementById('category_warning');
    
    if (!categorySelect) return; // 念のため要素が存在するかチェック
    
    // 全てのカテゴリ選択肢を保存
    const allCategoryOptions = Array.from(categorySelect.querySelectorAll('option')).map(opt => ({
        value: opt.value,
        text: opt.innerText,
        subject: opt.dataset.subject,
        grade: opt.dataset.grade,
        selected: opt.hasAttribute('selected') // サーバー側で選択状態かどうか
    }));
    
    // オーバーレイクリック時の警告表示
    if (categoryOverlay && categoryWarning) {
        categoryOverlay.addEventListener('click', function() {
            categoryWarning.style.display = 'block';
            setTimeout(() => {
                categoryWarning.style.display = 'none';
            }, 3000);
        });
    }
    
    function updateCategoryDropdown() {
        if (!subjectSelect || !gradeSelect) return;
        
        const subjectId = subjectSelect.value;
        const grade = gradeSelect.value;
        const currentCategory = categorySelect.value; // 現在の選択値（もしあれば）
        
        // 1. セレクトボックスをクリア
        categorySelect.innerHTML = '';
        
        // 2. デフォルトの「すべて」オプションを追加
        const defaultOpt = document.createElement('option');
        defaultOpt.value = "";
        defaultOpt.text = "すべて";
        categorySelect.appendChild(defaultOpt);
        
        // 3. 科目と学年が両方とも選択されていない場合は、カテゴリを無効化して終了
        if (!subjectId || !grade) {
            categorySelect.disabled = true;
            if (categoryOverlay) categoryOverlay.style.display = 'block';
            return;
        }
        
        // 4. 科目と学年が両方選択されていれば、有効化して絞り込んだ選択肢を追加
        categorySelect.disabled = false;
        if (categoryOverlay) categoryOverlay.style.display = 'none';
        if (categoryWarning) categoryWarning.style.display = 'none';
        let foundSelected = false;
        
        allCategoryOptions.forEach(opt => {
            if (!opt.value) return; // 元の「すべて」はスキップ
            
            // 科目と学年両方に合致するカテゴリを表示
            if (opt.subject === subjectId && opt.grade === grade) {
                const optionEl = document.createElement('option');
                optionEl.value = opt.value;
                optionEl.text = opt.text;
                
                // 元々サーバーから selected だったもの、または現在選択されているものを復元
                if (opt.value === currentCategory || (opt.selected && currentCategory === "")) {
                    optionEl.selected = true;
                    foundSelected = true;
                }
                
                categorySelect.appendChild(optionEl);
            }
        });
        
        // 以前の選択値が見つからなかった場合（絞り込み条件変更等）はデフォルトを選択
        if (!foundSelected) {
            categorySelect.value = "";
        }
    }
    
    // 科目または学年が変更されたときにカテゴリの選択肢を更新
    if (subjectSelect) subjectSelect.addEventListener('change', updateCategoryDropdown);
    if (gradeSelect) gradeSelect.addEventListener('change', updateCategoryDropdown);
    
    // ページ読み込み時に初期状態をセット
    updateCategoryDropdown();
});
