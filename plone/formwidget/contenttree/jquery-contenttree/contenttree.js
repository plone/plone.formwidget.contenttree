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
            })
        },
        contentTreeAdd: function(id, name, klass, title, base_path, multi_select) {
            var termCount = multi_select ? $('#' +id + '-input-fields').children().length : 0;


            $(this).parents(".contenttreeWindow").find('.navTreeCurrentItem > a').each(function () {
                var path = $(this).attr('href').substr(base_path.length);
                var field = $('#' + id + '-input-fields input[value="' + path + '"]');
                if(field.length == 0) {
                    if (multi_select) {
                        $('#' + id + '-input-fields').append('<span id="' + id + '-' + termCount + '-wrapper" class="option"><label for="' + id + '-' + termCount + '"><input type="checkbox" id="' + id + '-' + termCount + '" name="' + name + ':list" class="' + klass + '" title="' + title + '" checked="checked" value="' + path + '" /><span class="label">' + $.trim($(this).text()) + '</span></label></span>');
                    } else {
                        $('#' + id + '-input-fields').find(".option").remove();
                        $('#' + id + '-input-fields').append('<span id="' + id + '-' + termCount + '-wrapper" class="option"><label for="' + id + '-' + termCount + '"><input type="radio" id="' + id + '-' + termCount + '" name="' + name + ':list" class="' + klass + '" title="' + title + '" checked="checked" value="' + path + '" /><span class="label">' + $.trim($(this).text()) + '</span></label></span>');
                    }
                } else {
                    field.each(function() { this.checked = true });
                }
            });

            $(this).contentTreeCancel();
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
               
            if(o.folderEvent == undefined) o.folderEvent = 'click';
            if(o.selectEvent == undefined) o.selectEvent = 'click';
               
            if(o.expandSpeed == undefined) o.expandSpeed = -1;
            if(o.collapseSpeed == undefined) o.collapseSpeed = -1;
               
            if(o.multiFolder == undefined) o.multiFolder = true;
            if(o.multiSelect == undefined) o.multiSelect = false;

            o.root = $(this);

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
                if(!li.hasClass('navTreeCurrentItem')) {
                    var multi_key = ((event.ctrlKey) || (navigator.userAgent.toLowerCase().indexOf('macintosh') != -1 && event.metaKey));

                    if(!o.multiSelect || !multi_key) {
                        o.root.find('li.navTreeCurrentItem').removeClass('navTreeCurrentItem');
                    }

                    li.addClass('navTreeCurrentItem');
                    selected = true;
                } else {
                    li.removeClass('navTreeCurrentItem');
                    selected = false;
                }

                h(event, true, $(this).attr('href'), $.trim($(this).text()));
            }

            function bindTree(t) {
                $(t).find('li a').bind('click', function() { return false; });
                $(t).find('li.navTreeFolderish a').bind(o.folderEvent, handleFolderEvent);
                $(t).find('li.selectable a').bind(o.selectEvent, handleSelectEvent);
            }

            $(this).each(function() {
                bindTree($(this));
            });
        }
    });
    
})(jQuery);
