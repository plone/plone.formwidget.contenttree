$(function() {
    $('.plone-app-contenttree').each(function() {
	var div = $(this);
	var id = div.attr('inputid');
	var name = div.attr('inputname');
	var multiselect = div.attr('multiselect') == 'True';
	var basepath = div.attr('basepath');
	var tree = div.find('.plone-app-contenttree-tree');
	var loadurl = div.attr('loadurl');
	var searchurl = div.attr('searchurl');

	div.dialog({
	    resizable: false,
	    height: 340,
	    width: 480,
	    modal: true,
	    autoOpen: false,
	    position: 'center',
	    title: 'Browse content',
	    buttons: {
		"Add": function() {
		    var termCount = multiselect ? 
			$('#' + id + '-input-fields').children().length : 0;

		    var nodes = tree.dynatree('getSelectedNodes');
		    for (var i=0; i < nodes.length; i++) {
			var path = nodes[i].data.key.substr(basepath.length);
			var field = $('#' + id + '-input-fields input[value="' + path + '"]');

			if(field.length == 0) {
			    if (multiselect) {
				$('#' + id + '-input-fields').append('<span id="' + id + '-' + termCount + '-wrapper" class="option"><label for="'+id+'-'+termCount+'"><input type="checkbox" id="'+id+'-'+termCount+'" name="' + name + ':list" checked="checked" value="'+path+'" /><span class="label">'+nodes[i].data.title+'</span></label></span>');
			    } else {
				$('#'+id+'-input-fields').find(".option").remove();
				$('#'+id+'-input-fields').append('<span id="'+id+'-'+termCount+'-wrapper" class="option"><label for="'+id+'-'+termCount + '"><input type="radio" id="' + id + '-' + termCount + '" name="' + name + ':list" checked="checked" value="' + path + '" /><span class="label">' + nodes[i].data.title + '</span></label></span>');
			    }
			} else {
			    field.each(function() { this.checked = true });
			}
			termCount += 1;
		    };
		    $(this).dialog("close");
		},
		Cancel: function() {
		    $(this).dialog("close");
		}
	    }
	});
	
	tree.dynatree({
	    initAjax: {url: loadurl},
	    checkbox: true,
	    imagePath: '',
	    selectMode: multiselect ? 2 : 1,
	    onLazyRead: function(node){
		node.appendAjax({url: loadurl,
				 data: {"key": node.data.key}
				});
	    }
	});
	
	$('#'+ id + '-buttons-search').hide();
	$('#'+ id +'-widgets-query').after(
            $(document.createElement('input'))
            .attr({
                'type': 'button',
                'value': 'Search'
            })
            .addClass('searchButton')
            .click(function () {div.dialog('open');})
        );

	$('#'+ id + '-searchbtn').click(function() {
	    var root = tree.dynatree('getRoot');
	    root.removeChildren();
	    root.appendAjax({url: searchurl,
			     data: {"search": $('#'+ id + '-search').val()}
			    });
	});

	$('#'+ id + '-reloadbtn').click(function() {
	    var root = tree.dynatree('getRoot');
	    root.removeChildren();
	    root.appendAjax({url: loadurl});
	});

    });
});
