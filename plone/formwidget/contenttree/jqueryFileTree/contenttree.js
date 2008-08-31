// This is based on jQueryFileTree by   Cory S.N. LaViska
if(jQuery) (function($){
    
    $.extend($.fn, {
        contentTree: function(o, h) {

            // Defaults
            if(!o) var o = {};
            if(o.script == undefined) o.script = 'fetch';
               
            if(o.folderEvent == undefined) o.folderEvent = 'dblclick';
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
            
            function handleSelectEvent() {
                var li = $(this).parent();
                var selected = true;
                if(!li.hasClass('navTreeCurrentItem')) {
                    if(!o.multiSelect) {
                        o.root.find('li.navTreeCurrentItem').removeClass('navTreeCurrentItem');
                    }
                    
                    li.addClass('navTreeCurrentItem');
                    selected = true;
                } else {
                    li.removeClass('navTreeCurrentItem');
                    selected = false;
                }
                
                h($(this).attr('href'), $(this).attr('rel'), selected);
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