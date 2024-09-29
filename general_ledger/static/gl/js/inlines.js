
'use strict';
{


  $.fn.tabularFormset = function (selector, opts) {
    const options = $.extend({}, $.fn.tabularFormset.defaults, opts);
    console.log(options);
    // this is the table
    const $table = $(this);
    $(this).find("tbody > tr").addClass("original-form");


    const $tbody = $table.find('tbody');
    const $rows = $tbody.find('tr');
    console.log($rows);

    const totalForms = $("#id_" + options.prefix + "-TOTAL_FORMS").prop("autocomplete", "off");

    const initialForms = $("#id_" + options.prefix + "-INITIAL_FORMS").prop("autocomplete", "off");
    let nextIndex = parseInt(totalForms.val(), 10);
    const maxForms = $("#id_" + options.prefix + "-MAX_NUM_FORMS").prop("autocomplete", "off");
    const minForms = $("#id_" + options.prefix + "-MIN_NUM_FORMS").prop("autocomplete", "off");

    console.log(totalForms);
    console.log(initialForms);
    console.log(maxForms);
    console.log(minForms);


    let addButton;



    const updateElementIndex = function (el, prefix, ndx) {
      const id_regex = new RegExp("(" + prefix + "-(\\d+|__prefix__))");
      const replacement = prefix + "-" + ndx;
      if ($(el).prop("for")) {
        $(el).prop("for", $(el).prop("for").replace(id_regex, replacement));
      }
      if (el.id) {
        el.id = el.id.replace(id_regex, replacement);
      }
      if (el.name) {
        el.name = el.name.replace(id_regex, replacement);
      }
    };

    const inlineDeleteHandler = function (e1) {
      console.log(e1);
      e1.preventDefault();
      const deleteButton = $(e1.target);
      const row = deleteButton.closest('.' + options.formCssClass);
      const inlineGroup = row.closest('.inline-group');
      const rowIndex = $("." + options.formCssClass).index(row);
      console.log("Row index:", rowIndex);
      console.log("Row:", row);
      // remove the relevant row with non-field errors:
      const prevRow = row.prev();
      console.log(prevRow);
      if (prevRow.length && prevRow.hasClass('row-form-errors')) {
        prevRow.remove();
      }

      if (row.hasClass("original-form")) {
        // If the row is an original form, then we just hide it.
        $(`#id_${options.prefix}-${rowIndex}-DELETE`).prop("checked", true);
        $(`#id_${options.prefix}-${rowIndex}-DELETE`).val("on");

        row.hide();

      } else {
        row.remove();
        nextIndex -= 1;
      }

      // Pass the deleted form to the post-delete callback, if provided.
      if (options.removed) {
        options.removed(row);
      }

      // Trigger the formset:removed event.
      document.dispatchEvent(new CustomEvent("formset:removed", {
        detail: {
          formsetName: options.prefix
        }
      }));

      // Update the TOTAL_FORMS form count.
      const forms = $("." + options.formCssClass);
      console.log(forms);
      $("#id_" + options.prefix + "-TOTAL_FORMS").val(forms.length);
      // Show add button again once below maximum number.
      console.log($("#id_" + options.prefix + "-TOTAL_FORMS"));
      if ((maxForms.val() === '') || (maxForms.val() - forms.length) > 0) {
        //addButton.parent().show();
      }
      // Hide the remove buttons if at min_num.
      //toggleDeleteButtonVisibility(inlineGroup);
      // Also, update names and ids for all remaining form controls so
      // they remain in sequence:
      let i, formCount;
      const updateElementCallback = function () {
        updateElementIndex(this, options.prefix, i);
      };

      for (i = 0, formCount = forms.length; i < formCount; i++) {
        updateElementIndex($(forms).get(i), options.prefix, i);
        $(forms.get(i)).find("*").each(updateElementCallback);
      }
    };

    const addInlineDeleteButton = function (row) {
      if (row.is("tr")) {
        // If the forms are laid out in table rows, insert
        // the remove button into the last table cell:
        row.children(":last").append('<div><a class="' + options.deleteCssClass + '" href="#">' + options.deleteText + "</a></div>");
      } else if (row.is("ul") || row.is("ol")) {
        // If they're laid out as an ordered/unordered list,
        // insert an <li> after the last list item:
        row.append('<li><a class="' + options.deleteCssClass + '" href="#">' + options.deleteText + "</a></li>");
      } else {
        // Otherwise, just insert the remove button as the
        // last child element of the form's container:
        row.children(":first").append('<span><a class="' + options.deleteCssClass + '" href="#">' + options.deleteText + "</a></span>");
      }
      // Add delete handler for each row.
      row.find("a." + options.deleteCssClass).on('click', inlineDeleteHandler.bind(this));
    };


    const addInlineAddButton = function () {
      if (addButton === null) {
        if ($this.prop("tagName") === "TR") {
          // If forms are laid out as table rows, insert the
          // "add" button in a new table row:
          const numCols = $this.eq(-1).children().length;
          $parent.append('<tr class="' + options.addCssClass + '"><td colspan="' + numCols + '"><a href="#">' + options.addText + "</a></tr>");
          addButton = $parent.find("tr:last a");
        } else {
          // Otherwise, insert it immediately after the last form:
          $this.filter(":last").after('<div class="' + options.addCssClass + '"><a href="#">' + options.addText + "</a></div>");
          addButton = $this.filter(":last").next().find("a");
        }
      }
      addButton.on('click', addInlineClickHandler);
    };

    const addInlineClickHandler = function (e) {
      e.preventDefault();

      const formCopySource = $("#items-empty > tbody > tr");
      const formCopyTarget = $('#table-invoice-line-list > tbody');
      const newForm = formCopySource.clone(true);

      console.log("got here");
      console.log(options.emptyCssClass);
      console.log(options.formCssClass);
      console.log(nextIndex);

      console.log(formCopySource);
      console.log(formCopyTarget);

      newForm.removeClass(options.emptyCssClass)
        .addClass(options.formCssClass);
        //.attr("id", options.prefix + "-" + nextIndex);

      addInlineDeleteButton(newForm);

      newForm.find("*").each(function () {
        updateElementIndex(this, options.prefix, totalForms.val());
      });

      // Insert the new form when it has been fully edited.
      //newForm.insertAfter(formCopyTarget.find('tbody > tr:last'));
      formCopyTarget.append(newForm);
      // Update number of total forms.
      $(totalForms).val(parseInt(totalForms.val(), 10) + 1);
      nextIndex += 1;
      // Hide the add button if there's a limit and it's been reached.
      if ((maxForms.val() !== '') && (maxForms.val() - totalForms.val()) <= 0) {
        addButton.parent().hide();
      }
      // Show the remove buttons if there are more than min_num.
      //toggleDeleteButtonVisibility(row.closest('.inline-group'));

      // Pass the new form to the post-add callback, if provided.
      if (options.added) {
        options.added(newForm);
      }
      newForm.get(0).dispatchEvent(new CustomEvent("formset:added", {
        bubbles: true,
        detail: {
          formsetName: options.prefix
        }
      }));
    };

    // Create the delete buttons for all unsaved inlines:
    // $this.filter('.' + options.formCssClass + ':not(.has_original):not(.' + options.emptyCssClass + ')').each(function () {
    //   addInlineDeleteButton($(this));
    // });
    $rows.each(function () {
      addInlineDeleteButton($(this));
    });

    // Create the add button, initially hidden.
    addButton = options.addButton;
    addInlineAddButton();

  };





  /* Setup plugin defaults */
  $.fn.tabularFormset.defaults = {
    prefix: "form", // The form prefix for your django formset
    addText: "add another", // Text for the add link
    deleteText: "remove", // Text for the delete link
    addCssClass: "add-row", // CSS class applied to the add link
    deleteCssClass: "delete-row", // CSS class applied to the delete link
    emptyCssClass: "empty-row", // CSS class applied to the empty row
    formCssClass: "dynamic-form", // CSS class applied to each form in a formset
    added: null, // Function called each time a new form is added
    removed: null, // Function called each time a form is deleted
    addButton: null // Existing add button to use
  };

  $(document).ready(function () {
    $("#invoice-lines1").each(function () {
      console.log($(this).data())
      const data = $(this).data()
      let selector;
      switch (data.inlineType) {
        case "table":
          console.log("this is table");
          selector = "#table-invoice-line-list"
          console.log(selector);
          //console.log(inlineOptions.options.prefix);
          $(selector).tabularFormset(selector, {
            "prefix": "invoice_lines",
            "addButton": $("#add-line"),
          });
          break;
        default:
          console.error("didn't find it");
      }
    });
  });
}

// #items-group .tabular.inline-related tbody:first > tr.form-row
