odoo.define('lp_base_import_inh.import', function (require) {
    "use strict";
    var DataImport = require('base_import.import').DataImport;
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var QWeb = core.qweb;
    var DataImportInh = DataImport.include({
        import_options: function () {
            var res = this._super.apply(this, arguments);
            res['c_import'] = this.$('select.oe_import_c_import').val();
            return res
        },
        renderButtons: function () {
            var self = this;
            this.$buttons = $(QWeb.render("ImportView.buttons", this));
            this.$buttons.filter('.o_import_validate').on('click', this.validate.bind(this));
            this.$buttons.filter('.o_import_import').on('click', this.import.bind(this));
            this.$buttons.filter('.oe_import_file').on('click', function (e) {
                if (self.$('select.oe_import_c_import').val() == "") {
                    Dialog.alert(self, 'Please Select Template!');
                }
                else {
                    self.$('.o_content .oe_import_file').click();
                }
            });
            this.$buttons.filter('.o_import_cancel').on('click', function (e) {
                e.preventDefault();
                self.exit();
            });
        },
        events: {
            "click .my_class": "download_options",
            'change .oe_import_file': 'loaded_file',
            'change input.oe_import_has_header, .js_import_options input': 'settings_changed',
            'change input.oe_import_advanced_mode': function (e) {
                this.do_not_change_match = true;
                this['settings_changed']();
            },
            'click a.oe_import_toggle': function (e) {
                e.preventDefault();
                this.$('.oe_import_options').toggle();
            },
            'click .oe_import_report a.oe_import_report_count': function (e) {
                e.preventDefault();
                $(e.target).parent().parent().toggleClass('oe_import_report_showmore');
            },
            'click .oe_import_report_see_possible_value': function (e) {
                e.preventDefault();
                $(e.target).parent().toggleClass('oe_import_report_showmore');
            },
            'click .oe_import_moreinfo_action a': function (e) {
                e.preventDefault();

                var action = JSON.parse($(e.target).attr('data-action'));
                // FIXME: when JS-side clean_action
                action.views = _(action.views).map(function (view) {
                    var id = view[0], type = view[1];
                    return [
                        id,
                        type !== 'tree' ? type
                            : action.view_type === 'form' ? 'list'
                                : 'tree'
                    ];
                });
                this.do_action(_.extend(action, {
                    target: 'new',
                    flags: {
                        search_view: true,
                        display_title: true,
                        pager: true,
                        list: { selectable: false }
                    }
                }));
            },
        },
        download_options: function () {
            var userUrl = "";
            if (this.$('select.oe_import_c_import').val() == 'ooredoo') {
                userUrl = "/lp_base_import_inh/static/files/Ooredoo.xlsx";
                saveFile(userUrl);
            }
            if (this.$('select.oe_import_c_import').val() == 'virgin') {
                userUrl = "/lp_base_import_inh/static/files/VirginTemplate.xlsx";
                saveFile(userUrl);
            }
            if (this.$('select.oe_import_c_import').val() == 'diwan') {
                userUrl = "/lp_base_import_inh/static/files/Diwan.xlsx";
                saveFile(userUrl);
            }
            if (this.$('select.oe_import_c_import').val() == 'aramex') {
                userUrl = "/lp_base_import_inh/static/files/Aramex.xlsx";
                saveFile(userUrl);
            }
            if (this.$('select.oe_import_c_import').val() == 'lp-general') {
                userUrl = "/lp_base_import_inh/static/files/LP-General.xlsx";
                saveFile(userUrl);
            }
        },

    });
    return {
        DataImportInh: DataImportInh,
    };

});

function saveFile(url) {

    var filename = url.substring(url.lastIndexOf("/") + 1).split("?")[0];
    var xhr = new XMLHttpRequest();
    xhr.responseType = 'blob';
    xhr.onload = function () {
        var a = document.createElement('a');
        a.href = window.URL.createObjectURL(xhr.response);
        a.download = filename;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        delete a;
    };
    xhr.open('GET', url);
    xhr.send();
}

odoo.define('lp_base_import_inh.listView', function (require) {
    "use strict";
    var ImportButton = require('base_import.ImportMenu');
    var ListController = require('web.ListController');
    var ListControllerInh = ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            const self = this;

            if (this.$buttons) {
                this.getSession().user_has_group('lp_crm.lp_group_crm_director').then(function (is_director) {
                    if (is_director) {
                        let import_button = self.$buttons.find('.import-btn');
                        import_button && import_button.click(self.proxy('import_button'));
                    }
                    else {
                        self.getSession().user_has_group('lp_crm.lp_group_crm_project_manager').then(function (is_project_manager) {
                            if (is_project_manager) {
                                let import_button = self.$buttons.find('.import-btn');
                                import_button && import_button.click(self.proxy('import_button'));
                            }
                            else {
                                self.getSession().user_has_group('hr_timesheet.group_timesheet_manager').then(function (is_admin) {
                                    if (is_admin) {
                                        let import_button = self.$buttons.find('.import-btn');
                                        import_button && import_button.click(self.proxy('import_button'));
                                    }
                                    else {
                                        self.$buttons.find('.import-btn').remove();
                                    }
                                });
                            }
                        });
                    }
                });
            }
        },
        import_button: function () {
            const action = {
                type: 'ir.actions.client',
                tag: 'import',
                params: {
                    model: 'account.analytic.line',
                    context: this.model.loadParams.context,
                }
            };
            return this.do_action(action);
        }
    })
    return {
        ListControllerInh: ListControllerInh,
    };
});