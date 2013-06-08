// This is based on jQueryFileTree by   Cory S.N. LaViska
if(jQuery) (function($){

    $.extend($.fn, {
        showDialog: function() {
            $(document.body).append($(document.createElement("div")).addClass("contenttreeWindowBlocker"))
            this[0].oldparent = $(this).parent()[0]; // store old parent element
            $(".contenttreeWindowBlocker").before(this);
            $(this).show();
            $(this).width($(window).width() * 0.75);
            $(this).height($(window).height() * 0.75);
            $(this).css({
                'left': $(window).width() * 0.125,
                'top': $(window).height() * 0.125
            });
        },
        contentTreeAdd: function() {
            var contenttree_window = (this).parents(".contenttreeWindow");
            var input_box = $('#'+ contenttree_window[0].id.replace(/-contenttree-window$/,"-widgets-query"));
            contenttree_window.find('.navTreeCurrentItem > a').each(function () {
                formwidget_autocomplete_new_value(input_box,$(this).attr('href'),$.trim($(this).text()));
            });

            $(this).contentTreeCancel();
            input_box.parents('.datagridwidget-cell').triggerHandler('change');
        },
        contentTreeCancel: function() {
            $(".contenttreeWindowBlocker").remove();
            var popup = $(this).parents(".contenttreeWindow");
            popup.hide();
            $(popup[0].oldparent).append(popup);
            popup[0].oldparent = null;
        },
        contentTree: function(o, h) {

            // Defaults
            if(!o) var o = {};
            if(o.script == undefined) o.script = 'fetch';
            if(o.previewScript == undefined) o.previewScript = 'preview';

            if(o.folderEvent == undefined) o.folderEvent = 'click';
            if(o.selectEvent == undefined) o.selectEvent = 'click';

            if(o.expandSpeed == undefined) o.expandSpeed = -1;
            if(o.collapseSpeed == undefined) o.collapseSpeed = -1;

            if(o.multiFolder == undefined) o.multiFolder = true;
            if(o.multiSelect == undefined) o.multiSelect = false;

            function loadTree(c, t, r) {
                $(c).addClass('wait');
                $.post(o.script, { href: t, rel: r}, function(data) {
                    $(c).removeClass('wait').append(data);
                    $(c).find('ul:hidden').slideDown({ duration: o.expandSpeed });
                    bindTree(c);
                });
            }

            function handleFolderEvent() {
                var li = $(this).parent();
                if(li.hasClass('collapsed')) {
                    if(!o.multiFolder) {
                        li.parent().find('ul:visible').slideUp({ duration: o.collapseSpeed });
                        li.parent().find('li.navTreeFolderish').removeClass('expanded').addClass('collapsed');
                    }

                    if(li.find('ul').length == 0)
                        loadTree(li, escape($(this).attr('href')), escape($(this).attr('rel')));
                    else
                        li.find('ul:hidden').slideDown({ duration: o.expandSpeed });

                    li.removeClass('collapsed').addClass('expanded');
                } else {
                    li.find('ul').slideUp({ duration: o.collapseSpeed });
                    li.removeClass('expanded').addClass('collapsed');
                }
                return false;
            }

            function handleSelectEvent(event) {
                var li = $(this).parent();
                var selected = true;
                var root = $(this).parents('ul.navTree');
                if(!li.hasClass('navTreeCurrentItem')) {
                    var multi_key = ((event.ctrlKey) || (navigator.userAgent.toLowerCase().indexOf('macintosh') != -1 && event.metaKey));

                    if(!o.multiSelect || !multi_key) {
                        root.find('li.navTreeCurrentItem').removeClass('navTreeCurrentItem');
                    }

                    li.addClass('navTreeCurrentItem');
                    var preview_window = $('.contenttreePreview',$(li).parents('.contenttreeWindow')[0])[0];
                    loadPreview(preview_window, escape($(this).attr('href')), escape($(this).attr('rel')));
                    selected = true;
                } else {
                    li.removeClass('navTreeCurrentItem');
                    selected = false;
                }

                h(event, true, $(this).attr('href'), $.trim($(this).text()));
            }

            function loadPreview(c,t,r) {
                $(c).addClass('wait');
                $.post(o.previewScript, { href: t, rel: r}, function(data) {
                    $('.contenttreePreviewPane',c).replaceWith(data);
                    $(c).removeClass('wait');
                });
            }

            function bindTree(t) {
                $(t).find('li.navTreeFolderish a').unbind(o.folderEvent);
                $(t).find('li.selectable a').unbind(o.selectEvent);
                $(t).find('li a').bind('click', function() { return false; });
                $(t).find('li.navTreeFolderish a').bind(o.folderEvent, handleFolderEvent);
                $(t).find('li.selectable a').bind(o.selectEvent, handleSelectEvent);
            }

            // ----------------------------------------------------------------
            // Libarary selection event handling
            // ----------------------------------------------------------------
            // We need the contenttree window
            var ctwindow = $(this).parent('.contenttreeWindow');

            $('ul.formTabs li a', ctwindow).each(function() {
                $(this).bind('click', function() {
                    $('li a.selected', ctwindow).removeClass('selected');
                    $(this).addClass('selected');

                    // Remove old tree
                    $('.contenttreeWidget>ul', ctwindow).remove();

                    // Append new tree
                    console.log($(this).attr('href'));
                    loadTree($('.contenttreeWidget', ctwindow), $(this).attr('href'), 0);
                    return false;
                });
            });

            $('select[name="library"] option', ctwindow).each(function() {
                $(this).removeAttr('selected');
                $(this).bind('click', function() {
                    $(this).attr('selected', 'selected');

                    // Remove old tree
                    $('.contenttreeWidget>ul', ctwindow).remove();

                    // Append new tree
                    loadTree($('.contenttreeWidget', ctwindow), escape($(this).attr('value')), 0);
                    return false;
                });
            });

            if ($(this).children('ul.navTree').length <= 0) {
                $(this).each(function() {
                    loadTree(this, o.rootUrl, 0);
                });
            } else {
                $(this).each(function() {
                    bindTree($(this));
                });
           }

        }
    });

})(jQuery);
