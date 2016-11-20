/**
 * jquery.tgHierSelectV2
 * 
 * 【概要】
 * 階層としているプルダウンを選択値により連動させるjQueryプラグインです。
 *  
 * 【親子の関連付け方法】
 * 子のクラス名に、"p'親のvalue'" を付与して下さい。
 *（例：p1)
 * 
 * 【セレクトメニューの命名規則】
 * selectのnameは任意でOK。idは必ず「lv」を接頭語とし、以下数値を付ける形で一意の名称にして下さい。
 * 連動させるセレクトメニューには同じclass名を付けて下さい。
 *（例：<select name="sample1" id="lv1" class="group1"> ）
 * 
 * 【HTMLに記載するオプションの記述方法】
 *  $(document).ready(function(){
 *      $(this).tgHierSelectV2({
 *          group: 'group1',          ←★グループ名
 *          maxLevel: '5',            ←★最下層とするセレクトメニューの階層数。この場合は5階層となる
 *          defaultSelect: '▼選択',  ←★デフォルトのオプション内容
 *      });
 *  });
 * 
 * @Copyright : 2014 toogie | http://wataame.sumomo.ne.jp/archives/5124
 * @Version   : 2.0
 * @Modified  : 2014-04-28
 * 
 */

;(function($){
    $.fn.tgHierSelectV2 = function(options){

        var opts = $.extend({}, $.fn.tgHierSelectV2.defaults, options);
        var cnt;
        var arr = [];

        $('html').find('select.'+opts.group).each( function(){

            // nameのレベル番号取得
            var lvTxt = parseInt($(this).attr('id').replace(/lv/, ""));

            // プルダウンのoption内容をコピー
            arr[lvTxt] = $('#lv'+lvTxt+' option').clone();

            // プルダウン選択時処理
            $('#'+this.id).change( function(){

                // プルダウン選択値
                var pdVal = $(this).val();

                // レベル文字を取得し数値化
                var currentLvNum = parseInt($(this).attr('id').replace(/lv/, ""));
                var nextLevelNum = currentLvNum+1;

                // プルダウン操作
                $('#lv'+nextLevelNum).removeAttr("disabled");                   // 子プルダウンの"disabled"解除
                $('#lv'+nextLevelNum+" option").remove();                       // 一旦、子プルダウンのoptionを削除
                $(arr[currentLvNum+1]).appendTo('#lv'+nextLevelNum);            // (コピーしていた)元の子プルダウンを表示
                $('#lv'+nextLevelNum+" option[class != p"+pdVal+"]").remove();  // 選択値以外のクラスのoptionを削除

                // デフォルトのoptionを先頭に表示
                for(cnt=nextLevelNum; cnt<=opts.maxLevel; cnt++){
                    $('#lv'+cnt).prepend('<option value="0" selected="selected">'+opts.defaultSelect+'</option>');
                }
                // 変更したプルダウン以下の子プルダウンを全てdisabledに
                if((nextLevelNum+1) <= opts.maxLevel){
                    for(i=nextLevelNum+1; i<=opts.maxLevel; i++){
                        $('#lv'+i).attr("disabled", "disabled");
                    }
                }
            });
        });
    }
})(jQuery);