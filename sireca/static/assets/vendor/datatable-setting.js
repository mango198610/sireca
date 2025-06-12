var idtabla = 0; // tabla con la que se está interactuando

$('document').ready(function(){
	$('.data-table').DataTable({
		scrollCollapse: true,
		autoWidth: false,
		responsive: true,
		columnDefs: [{
			targets: "datatable-nosort",
			orderable: false,
		}],
		"lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],

		"language": {
			 emptyTable: "No se encontró ningun dato disponible.", // Cambia el mensaje aquí
			"info": "_START_-_END_ of _TOTAL_ entries",
			searchPlaceholder: "Search",
			paginate: {
				next: '<i class="ion-chevron-right"></i>',
				previous: '<i class="ion-chevron-left"></i>'
			}
		},
	});
    $('.data-table-nuevo').DataTable({
		language: {
			url: '../ube/static/vendors/scripts/datatable_espanol.json',
		},
        autoWidth: true,
        // responsive: false,
        //scrollX: true,
        info: false,
        search: true,
        searchable: false,
        searching: false,
        lengthMenu: false,
        lengthChange: false,
        pageLength: -1,
        // columnDefs: [{
        //     targets: "datatable-nosort",
        //     orderable: false,
        // }],
        // fixedHeader: {
			// header: true,
			// footer: false,
			// headerOffset: $('.header').outerHeight()
        // },
    });

	$('.data-table-export').DataTable({
		scrollCollapse: true,
		autoWidth: false,
		responsive: true,
		columnDefs: [{
			targets: "datatable-nosort",
			orderable: false,
		}],
		"lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
		"language": {
			"info": "_START_-_END_ of _TOTAL_ entries",
			searchPlaceholder: "Search",
			paginate: {
				next: '<i class="ion-chevron-right"></i>',
				previous: '<i class="ion-chevron-left"></i>'
			}
		},
		dom: 'Bfrtp',
		buttons: [
		'copy', 'csv', 'pdf', 'print'
		]
	});

	var table = $('.select-row').DataTable();
	$('.select-row tbody').on('click', 'tr', function () {
		if ($(this).hasClass('selected')) {
			$(this).removeClass('selected');
		}
		else {
			table.$('tr.selected').removeClass('selected');
			$(this).addClass('selected');
		}
	});

	var multipletable = $('.multiple-select-row').DataTable();
	$('.multiple-select-row tbody').on('click', 'tr', function () {
		$(this).toggleClass('selected');
	});
	var table = $('.checkbox-datatable').DataTable({
		'scrollCollapse': true,
		'autoWidth': false,
		'responsive': true,
		"lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
		"language": {
			"info": "_START_-_END_ of _TOTAL_ entries",
			searchPlaceholder: "Search",
			paginate: {
				next: '<i class="ion-chevron-right"></i>',
				previous: '<i class="ion-chevron-left"></i>'
			}
		},
		'columnDefs': [{
			'targets': 0,
			'searchable': false,
			'orderable': false,
			'className': 'dt-body-center',
			'render': function (data, type, full, meta){
				return '<div class="dt-checkbox"><input type="checkbox" name="id[]" value="' + $('<div/>').text(data).html() + '"><span class="dt-checkbox-label"></span></div>';
			}
		}],
		'order': [[1, 'asc']]
	});

	$('#example-select-all').on('click', function(){
		var rows = table.rows({ 'search': 'applied' }).nodes();
		$('input[type="checkbox"]', rows).prop('checked', this.checked);
	});

	$('.checkbox-datatable tbody').on('change', 'input[type="checkbox"]', function(){
		if(!this.checked){
			var el = $('#example-select-all').get(0);
			if(el && el.checked && ('indeterminate' in el)){
				el.indeterminate = true;
			}
		}
	});


	// ---------- BOTONES LATERALES PARA DESPLAZAR LAS TABLAS ----------- //
	$(document).on("click", "#scrollLeft", function () {
		scrollLeft();
	});

	$(document).on("click", "#scrollRight", function () {
		scrollRight();
	});

	let scrollInterval;
	$(document).on("mousedown", "#scrollLeft", function () {
		scrollInterval = setInterval(scrollLeft, 150);
	}).on("mouseup mouseleave", "#scrollLeft", function () {
		clearInterval(scrollInterval);
	});

	$(document).on("mousedown", "#scrollRight", function () {
		scrollInterval = setInterval(scrollRight, 150);
	}).on("mouseup mouseleave", "#scrollRight", function () {
		clearInterval(scrollInterval);
	});


	// Escucha los cambios de tamaño de la ventana
	window.addEventListener('resize', function () {
        habilitaScroll();
		$.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
        $.fn.dataTable.tables({ visible: true, api: true }).fixedHeader.adjust();
	});

	// Escucha si el mouse esta apuntando la tabla
	/*$(document).on("mouseenter", "table", function () {
		detectMouseOnTable();
		console.log('en tabla');
	}).on('mouseleave', "table", function () {
		if (!$("table").is(':hover')) {
			detectMouseOutTable();
			console.log('fuera tabla');
		}
	});*/
	$('table').on('mouseenter', function () {
		detectMouseOnTable();
	}).on('mouseleave', function () {
		const isHovered = $(this).is(':hover');
		if (!isHovered) {
			detectMouseOutTable();
		}
	});


	$(document).on("mouseenter", "#scrollLeft", function () {
		detectMouseOnTable();
	});

	$(document).on("mouseenter", "#scrollRight", function () {
		detectMouseOnTable();
	});


});

function datatTablaServerSide(id, ajaxUrl, ajaxData, columnas, columnasCentradas){
	var tabledata = $('#'+id).DataTable({
		language: {
			url: '../ube/static/vendors/scripts/datatable_espanol.json',
		},
		orderCellsTop  : true,
		scrollCollapse: true,
		autoWidth: true,
		responsive: false,
		paging: true,
		searching: true,
		search: true,
		info: false,
		processing: true,
		serverSide: true,
		ordering: true,
		scrollX: true,
		lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
		ajax: {
			url: ajaxUrl,
			type: 'POST',
			retries: 10  ,
			data: function (data) {
				$.each(ajaxData, function (key, value) {
					data[key] = value;
					if(key === 'parametrosAdicionales'){
						let parametroadicional = data[key]
						$.each(parametroadicional, function (keyAdicional, valueAdicional) {
							data[keyAdicional] = $('#'+valueAdicional).val()
						});
					}
				});
				//return d;
			},
			dataSrc: function (response) {
				if (response.result === 'ok') {
					$('#' + id +'_processing').css('display','none')
					return response.data
				} else {
					//TODO personalizar mensajes error desde el json de python
					Swal.fire({
						title: 'Se produjo un error al cargar los datos.',
						html:'<span class="text-muted"> Intente cargar de nuevo, si el problema persiste intentelo mas tarde.</span>',
						icon: 'error',
						showCancelButton: false,
						confirmButtonText: 'Volver a cargar',
						cancelButtonText: 'No',
						preConfirm: () => {
							$('#'+id+'_processing').css('visibility', 'visible');
							return $('#' + id).DataTable().ajax.reload();
						},
					});
					$('#' + id +'_processing').css('display','none');
					 return [];
				}
			},
			error: function (xhr, textStatus, errorThrown) {
				//TODO personalizar mensajes error desde el json de python
                if (this.retries-- > 0) {
                    $.ajax(this);
                } else {
                    Swal.fire({
                        title: 'Se produjo un error de conexión.',
                        html: '<span class="text-muted"> Intente cargar de nuevo, si el problema persiste intentelo mas tarde.</span>',
                        icon: 'error',
                        showCancelButton: false,
                        confirmButtonText: 'Volver a cargar',
                        cancelButtonText: 'No',
                        preConfirm: () => {
                            $('#' + id + '_processing').css('visibility', 'visible');
                            return $('#' + id).DataTable().ajax.reload();
                        },
                    });
                    $('#' + id + '_processing').css('display', 'none');
                    return [];
                }

			},
		},
		columns: columnas,
		columnDefs: columnasCentradas,
		fixedHeader: true, // Mantener la cabecera fija --
		initComplete: function () {
            $('#' + id + '_length').css('float', 'left');
            $('#' + id + '_length').parent().removeClass('col-md-6').addClass('col-md-12').append($('<a href="javascript:void(0);" onclick="limpiarFiltrosDatatable(\'' + id + '\')" data-toggle="tooltip" title="Limpiar Filtros de Busqueda" class="d-none btn btn-outline-info float-right mr-3">' +
                '<i class="icon-copy dw dw-refresh1"></i> Limpiar' +
                '</a>'));

			$('.dataTables_scrollBody').css('position','unset');
			var table = this.api();
			var clasesArraySelect2  = []

			$('.filtro-columna', table.table().header()).each(function () {
				var columnIndex = $(this).index();
				var filtroSelect = $(this).is('[class*="filtro-select"]');
				var filtroFecha = $(this).hasClass('filtro-fecha');
				if(! $(this).hasClass('sin-filtrado')){
					if(filtroSelect){
						var classes = this.className.split(' ');

						var claseFiltro = classes.find(function (clase) {
							return clase.includes('filtro-select');
						});
						clasesArraySelect2.push(claseFiltro)

						var html = $('<select class="custom-select2 form-control form-control-sm " style="width: 100%"><option value="">TODOS</option></select>')
							.on('change', function () {
								var val = $.fn.dataTable.util.escapeRegex(
									$(this).val()
								);
								table.column(columnIndex).search(val ? val : '', true, false).draw();
							});

						var filtro = table.ajax.json()[claseFiltro];
						for (var i in filtro) {
							var f = filtro[i];
							html.append('<option value="' + f.id + '">' + f.nombre + '</option>');
						}

					}else if(filtroFecha){
						var html = $('<div class="d-flex"></div>')
							.append($('<input type="date" class="form-control form-control-sm" />')
								.on('change', function () {
									table.column(columnIndex).search($(this).val()).draw();
								})
							)


					}else{
						var html = $('<input type="text" class="form-control form-control-sm form-control-filter" placeholder="Filtrar..."/>')
							.on('keyup change', function () {
								table.column(columnIndex).search($(this).val()).draw();
							});
					}

					$(this).html(html);
				}
			});
			if (clasesArraySelect2) {
				for (var c in clasesArraySelect2) {
					$("." + clasesArraySelect2[c] + " select").select2({
						dropdownParent: $('#' + id)
					});

				}
			}

			$('#' + id + '_filter').parent().addClass('d-none')
			$('#'+ id +'_filter').find('label input').attr('id','search_' + id)
			$(".custom-select").select2({
				dropdownParent: $('#' + id + '_wrapper').find('.dataTables_scrollBody') ? $('#' + id + '_wrapper ').find('.dataTables_scrollHead') :  $('#' + id + '_wrapper ').find('.dt-scroll-body')
			});

			table.columns.adjust(); // Ajustar las columnas después de la carga --
		}
	});
	$('#' + id).on('draw.dt', function () {
		var api = $('#' + id).DataTable();
		var json = api.ajax.json();
        if (json.filtrado)
            $('#' + id + '_length').next().removeClass('d-none')
        else
            $('#' + id + '_length').next().addClass('d-none')
		$('#total_registros').html('<b>Total registros:</b> '+json.recordsTotal)
		$('#total_registros_filtrado').html('<b>Total registros filtrados:</b> '+json.recordsFiltered)
		$('.dtfc-fixed-end').css('z-index','0 !important')
		$('#'+id+'_filter').find('label').css('display','none')

		$('#' + id).on('processing.dt', function (e, settings, processing) {
			if (processing) {
				$('#' + id +'_processing').css('display','flex')
			}else{
				$('#' + id +'_processing').css('display','none')
			}
		});

		habilitaScroll();
		detectMouseOutTable();
	});

	return tabledata;
}
function datatTablaServerSideNuevo(id, ajaxUrl, ajaxData, columnas, columnasCentradas, options) {
	var tabledata = $('#'+id).DataTable({
		language: {
			url: '../ube/static/vendors/scripts/datatable_espanol.json',
		},
		// orderCellsTop  : true,
		// scrollCollapse: true,
		autoWidth: true,
		// responsive: false,
		paging: true,
		searching: true,
		search: true,
		info: false,
		processing: true,
		serverSide: true,
		scrollX: true,
	   	pageLength: options.pageLength,
		lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
		order: options.order,
		ordering: options.order,
		fixedHeader: {
			header: true,
			footer: false,
			headerOffset: $('.header').outerHeight()
		},
		ajax: {
			url: ajaxUrl,
			type: 'POST',
			retries: 10  ,
			data: function (data) {
				$.each(ajaxData, function (key, value) {
					data[key] = value;
					if(key === 'parametrosAdicionales'){
						let parametroadicional = data[key]
						$.each(parametroadicional, function (keyAdicional, valueAdicional) {
							data[keyAdicional] = $('#'+valueAdicional).val()
						});
					}
				});
				//return d;
			},
			dataSrc: function (response) {
				if (response.result === 'ok') {
					$('#' + id +'_processing').css('display','none')
					return response.data
				} else {
					//TODO personalizar mensajes error desde el json de python
					Swal.fire({
						title: 'Se produjo un error al cargar los datos.',
						html:'<span class="text-muted"> Intente cargar de nuevo, si el problema persiste intentelo mas tarde.</span>',
						icon: 'error',
						showCancelButton: false,
						confirmButtonText: 'Volver a cargar',
						cancelButtonText: 'No',
						preConfirm: () => {
							$('#'+id+'_processing').css('visibility', 'visible');
							return $('#' + id).DataTable().ajax.reload();
						},
					});
					$('#' + id +'_processing').css('display','none');
					 return [];
				}
			},
			error: function (xhr, textStatus, errorThrown) {
				//TODO personalizar mensajes error desde el json de python
                if (this.retries-- > 0) {
                    $.ajax(this);
                } else {
                    Swal.fire({
                        title: 'Se produjo un error de conexión.',
                        html: '<span class="text-muted"> Intente cargar de nuevo, si el problema persiste intentelo mas tarde.</span>',
                        icon: 'error',
                        showCancelButton: false,
                        confirmButtonText: 'Volver a cargar',
                        cancelButtonText: 'No',
                        preConfirm: () => {
                            $('#' + id + '_processing').css('visibility', 'visible');
                            return $('#' + id).DataTable().ajax.reload();
                        },
                    });
                    $('#' + id + '_processing').css('display', 'none');
                    return [];
                }

			},
		},
		columns: columnas,
		//columnDefs: columnasCentradas,
		initComplete: function () {

            $('#' + id + '_length').css('float', 'left');
            $('#' + id + '_length').parent().removeClass('col-md-6').addClass('col-md-12').append($('<a href="javascript:void(0);" onclick="limpiarFiltrosDatatable(\'' + id + '\')" data-toggle="tooltip" title="Limpiar Filtros de Busqueda" class="d-none btn btn-outline-info float-right mr-3">' +
                '<i class="icon-copy dw dw-refresh1"></i> Limpiar' +
                '</a>'));

			$('.dataTables_scrollBody').css('position','unset');
			var table = this.api();
			var clasesArraySelect2  = [];

			$('.filtro-columna', table.table().header()).each(function () {
				var columnIndex = $(this).index();
				var filtroSelect = $(this).is('[class*="filtro-select"]');
				var filtroFecha = $(this).hasClass('filtro-fecha');
				if(! $(this).hasClass('sin-filtrado')){
					if(filtroSelect){
						var classes = this.className.split(' ');

						var claseFiltro = classes.find(function (clase) {
							return clase.includes('filtro-select');
						});
						clasesArraySelect2.push(claseFiltro)

						var html = $('<select class="custom-select2 form-control form-control-sm " style="width: 100%"><option value="">TODOS</option></select>')
							.on('change', function () {
								var val = $.fn.dataTable.util.escapeRegex(
									$(this).val()
								);
								table.column(columnIndex).search(val ? val : '', true, false).draw();
							});

						var filtro = table.ajax.json()[claseFiltro];
						for (var i in filtro) {
							var f = filtro[i];
							html.append('<option value="' + f.id + '">' + f.nombre + '</option>');
						}

					}else if(filtroFecha){
						var html = $('<div class="d-flex"></div>')
							.append($('<input type="date" class="form-control form-control-sm" />')
								.on('change', function () {
									table.column(columnIndex).search($(this).val()).draw();
								})
							)


					}else{
						var html = $('<input type="text" class="form-control form-control-sm form-control-filter" placeholder="Filtrar..."/>')
							.on('keyup change', function () {
								table.column(columnIndex).search($(this).val()).draw();
							});
					}

					$(this).html(html);
				}
			});
			if (clasesArraySelect2) {
				for (var c in clasesArraySelect2) {
					$("." + clasesArraySelect2[c] + " select").select2({
						dropdownParent: $('#' + id)
					});

				}
			}

			$('#' + id + '_filter').parent().addClass('d-none')
			$('#'+ id +'_filter').find('label input').attr('id','search_' + id)
			$(".custom-select").select2({
				dropdownParent: $('#' + id + '_wrapper').find('.dataTables_scrollBody') ? $('#' + id + '_wrapper ').find('.dataTables_scrollHead') :  $('#' + id + '_wrapper ').find('.dt-scroll-body')
			});

			$.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
			$.fn.dataTable.tables({ visible: true, api: true }).fixedHeader.adjust();
		}
	});
	$('#' + id).on('draw.dt', function () {

		$('#'+id+'_wrapper').find('[id^=dt-length-]').select2();
		var api = $('#' + id).DataTable();
		var json = api.ajax.json();
        if (json.filtrado)
            $('#' + id + '_length').next().removeClass('d-none')
        else
            $('#' + id + '_length').next().addClass('d-none')
		$('#total_registros').html('<b>Total registros:</b> '+json.recordsTotal)
		$('#total_registros_filtrado').html('<b>Total registros filtrados:</b> '+json.recordsFiltered)
		$('.dtfc-fixed-end').css('z-index','0 !important')
		$('#'+id+'_filter').find('label').css('display','none')

		$('#' + id).on('processing.dt', function (e, settings, processing) {
			if (processing) {
				$('#' + id +'_processing').css('display','flex')
			}else{
				$('#' + id +'_processing').css('display','none')
			}
		});

		habilitaScroll();
		detectMouseOutTable();
		$.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
		$.fn.dataTable.tables({ visible: true, api: true }).fixedHeader.adjust();
		adjustTableHeight();
	});

	return tabledata;
}

limpiarFiltrosDatatable = function (table) {
	let thFiltros = null;
	if($('#' + table + '_wrapper').find('.dataTables_scrollHead'))
		thFiltros = $('#' + table + '_wrapper').find('.dataTables_scrollHead thead tr:nth-child(2) th ');
	else if($('#' + table + '_wrapper').find('.dt-scroll-body'))
		thFiltros = $('#' + table + '_wrapper').find('.dt-scroll-body thead tr:nth-child(2) th ');

	thFiltros.each(function (index, column) {
		$(column).find('input').each(function (index, elemento) {
			if ($(elemento).val() !== '' && $(elemento).val() !== undefined) {
				$(elemento).val('').trigger('change')
			}
		})
		$(column).find('select').each(function (index, elemento) {
			if ($(elemento).val() !== '' && $(elemento).val() !== undefined && $(elemento).val() !== '0') {
				$(elemento).val('').trigger('change')
			}
		})
	});
	$('.filtro-personalizado').each(function (index, elemento) {
		if ($(elemento).val() !== '0' || $(elemento).val() !== ''  && $(elemento).val() !== undefined) {
			if($(elemento).is('input')){
				$(elemento).val('').trigger('change')
				$('#search_'+table).val('').trigger('keyup');
			}else if($(elemento).is('select')) {
				$(elemento).val($(elemento).children().eq(0).val()).trigger('change')
			}
		}
	})
}


function habilitaScroll() {
	// crea los botones para desplazar la tabla
	let tableContainer = null;
	if(document.querySelector('.dataTables_scrollBody')){
		tableContainer = document.querySelector('.dataTables_scrollBody');
		idtabla = tableContainer.parentElement.parentElement.parentElement.parentElement.id;
	}
	else if(document.querySelector('.dt-scroll-body')){
		tableContainer = document.querySelector('.dt-scroll-body');
		idtabla = tableContainer.parentElement.parentElement.parentElement.parentElement.id;
	}
	// div donde está el id de la tabla
	const btn_scrollLeft = document.getElementById('scrollLeft');
	const btn_scrollRight = document.getElementById('scrollRight');
	if (tableContainer.scrollWidth > tableContainer.clientWidth){
		if (btn_scrollRight) {
			$("#scrollLeft").removeClass('d-none');
			$("#scrollRight").removeClass('d-none');
		} else {
			$("#"+idtabla).append('<div><button class="scroll-button scroll-button-left" id="scrollLeft">◄</button>\n' +
					 '<button class="scroll-button scroll-button-right" id="scrollRight">►</button></div>');
		}
	} else {
		if (btn_scrollLeft) {
			$("#scrollLeft").addClass('d-none');
			$("#scrollRight").addClass('d-none');
		}
	}
}

function scrollLeft() {
	const scrollAmount = 100; // Cantidad de desplazamiento en píxeles por clic

	let tableContainer = null;
	if(document.querySelector('.dataTables_scrollBody'))
		tableContainer = document.querySelector('.dataTables_scrollBody');
	else if(document.querySelector('.dt-scroll-body'))
		tableContainer = document.querySelector('.dt-scroll-body');
	if (tableContainer) {
		tableContainer.scrollLeft -= scrollAmount;
	}
}

function scrollRight() {
	const scrollAmount = 100; // Cantidad de desplazamiento en píxeles por clic
	let tableContainer = null;
	if(document.querySelector('.dataTables_scrollBody'))
		tableContainer = document.querySelector('.dataTables_scrollBody');
	else if(document.querySelector('.dt-scroll-body'))
		tableContainer = document.querySelector('.dt-scroll-body');
	if (tableContainer) {
		tableContainer.scrollLeft += scrollAmount;
	}
}


function detectMouseOnTable() {
	const btn_scrollLeft = document.getElementById('scrollLeft');
	const btn_scrollRight = document.getElementById('scrollRight');
	if (btn_scrollLeft && btn_scrollRight) {
		btn_scrollLeft.style.display = 'block';
		btn_scrollRight.style.display = 'block';
	}
}

function detectMouseOutTable() {
	const btn_scrollLeft = document.getElementById('scrollLeft');
	const btn_scrollRight = document.getElementById('scrollRight');
	if (btn_scrollLeft && btn_scrollRight) {
		btn_scrollLeft.style.display = 'none';
		btn_scrollRight.style.display = 'none';
	}
}

function adjustTableHeight() {
	var dtScrollBody = document.querySelector('.dt-scroll-body');
	dtScrollBody.style.position = 'unset';
}