// サーバーから単語リストを受け取る
let word_list = {{ word_list | safe }};

// スコアを記録するクラスを定義
class ScoreRecord {
  constructor(current_word) {
    this.index = 0;
    this.correct_ans = [];
    this.current_word = current_word;
  }
}

// 現在の単語セットを取得
var current_word = word_list[0];

// スコアオブジェクトを生成
const score_record = new ScoreRecord(current_word);

// プログレスバーを取得
var progress_bar = document.getElementById("progress-bar");

// 言語の出力先のpタグを取得
var word_to_learn = document.getElementById("word-to-learn");

// 出力するテキストを用意
var word_text = document.createTextNode(current_word.{{lang}});

// 単語を出力
word_to_learn.appendChild(word_text);

// 「答え合わせをする」ボタンと,答えを表示するpタグを取得
var check_ans = document.getElementById("check-ans");
var word_answer = document.getElementById("word-answer");

// 「覚えた」ボタンと「わからなかった」ボタンをそれぞれIDで取得、それぞれイベントリスナーを追加
var memorized = document.getElementById("memorized");
var notmemorized = document.getElementById("notmemorized");

memorized.addEventListener("click", function () {
    score_record.correct_ans.push(score_record.current_word);
});

memorized.addEventListener("click", nextWord);
notmemorized.addEventListener("click", nextWord);

// 「結果を見る」「次へ」ボタンを取得
var showresult = document.getElementById("showresult");
// var next_btn = document.getElementById("next-btn")

// 以下に「答え合わせをする」ボタンがクリックされた時の処理を定義。
check_ans.addEventListener("click", function() {
    // ボタンを非表示にする
    check_ans.style.display = "none";

    // 次の単語のindexを設定
    score_record.index += 1;

    // 答え（和訳）を取得、表示
    var answer_text = document.createTextNode(score_record.current_word.ja);
    word_answer.appendChild(answer_text);

    // 他のボタンのdisplayプロパティをそれぞれ変更
    memorized.style.display = "block";
    notmemorized.style.display = "block";
});

// 次の単語を表示する時のfunctionを定義
function nextWord () {
    // プログレスバーの長さを変更
    progress_bar.style.width = `${1/word_list.length * 100 * score_record.index}%`;

    // 下層ボタンの両方を非表示
    memorized.style.display = "none";
    notmemorized.style.display = "none";

    // 次の単語を取得
    score_record.current_word = word_list[score_record.index];

    if (score_record.index < word_list.length){
        // 次の単語を表示
        word_to_learn.innerHTML = '';
        word_answer.innerHTML = '';
        word_text = document.createTextNode(score_record.current_word.{{lang}});
        word_to_learn.appendChild(word_text);

        // カウントダウンタイマーをリセット
        reset_timer();

        //「答え合わせ」ボタンを表示
        check_ans.style.display = "block";
    } else {
        // 「結果を見る」ボタンを表示、文字をFinishに変更
        showresult.style.display = "block";
        word_to_learn.innerHTML = "";
        word_answer.innerHTML = "";
        word_to_learn.appendChild(document.createTextNode("Finish!"));

        // カウントダウンタイマーをリセット
        cd_timer.innerHTML = "";
        cd_timer.appendChild(document.createTextNode("05:00"));
    }
}

// next_btn.addEventListener("click", function(){
//     var result_input = document.getElementById("result-input");
//     var wordlist_input = document.getElementById("wordlist-input");
//     result_input.value = JSON.stringify(score_record.correct_ans);
//     wordlist_input.value = JSON.stringify(word_list);
//     this.style.display = "none";
//     showresult.style.display = "block";
// });

showresult.addEventListener("click", function(){
    var result_input = document.getElementById("result-input");
    var wordlist_input = document.getElementById("wordlist-input");
    var langname_input = document.getElementById("langname-input");
    // var wordindex_input = document.getElementById("wordindex-input");

    result_input.value = JSON.stringify(score_record.correct_ans);
    wordlist_input.value = JSON.stringify(word_list);
    langname_input.value = "{{lang}}";
    // wordindex_input.value = {{index}};

    // xhr = new XMLHttpRequest();
    // xhr.open("POST", "{{url_for('result', lang=lang, index=index)}}", false);
    // xhr.send(`result=${score_record.correct_ans}&word_list=${word_list}`);
    });

    ////////////////////////// Cound Down Timer ////////////////////////////////
    let cd_timer = document.getElementById("cd-timer");
    let answer_time = 500;
    let answer_seconds = 5;

    function reset_timer() {
        cd_timer.innerHTML = "";
        cd_timer.appendChild(document.createTextNode("05:00"));
        answer_time = 500;
        answer_seconds = 5;
        setTimeout(count_down, 100);
    }

    function count_down () {
        cd_timer.innerHTML = "";

        if (answer_time % 100 === 0) {
            answer_seconds -= 1;
        }

        answer_time -= 1;

        var current_time = zeroPadding(answer_seconds, 2) + ":" + zeroPadding(answer_time, 2);

        cd_timer.appendChild(document.createTextNode(current_time));

        var timer = setTimeout(count_down, 10);

        check_ans.addEventListener("click", function() {
            clearTimeout(timer);
        });

        if (answer_time === 0) {
            clearTimeout(timer);
        }
    }

    function zeroPadding(number, length){
        var zero = "";
        for (var i = 0; i < length; i++) {
            zero += "0";
            // console.log(zero)
            // console.log("num: " + number)
        }
        return ( zero + number ).slice( -length );
    }

    window.onload = function () {
        setTimeout(reset_timer(),3000);
    };
