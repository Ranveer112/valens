use chrono::prelude::*;
use seed::{prelude::*, *};

use crate::common;
use crate::data;

// ------ ------
//     Init
// ------ ------

pub fn init(mut url: Url, orders: &mut impl Orders<Msg>, data_model: &data::Model) -> Model {
    let base_url = url.to_hash_base_url();

    if url.next_hash_path_part() == Some("add") {
        orders.send_msg(Msg::ShowAddPeriodDialog);
    }

    orders.subscribe(Msg::DataEvent);

    let (first, last) = common::initial_interval(
        &data_model
            .period
            .iter()
            .map(|bf| bf.date)
            .collect::<Vec<NaiveDate>>(),
    );

    Model {
        base_url,
        interval: common::Interval { first, last },
        dialog: Dialog::Hidden,
        loading: false,
    }
}

// ------ ------
//     Model
// ------ ------

pub struct Model {
    base_url: Url,
    interval: common::Interval,
    dialog: Dialog,
    loading: bool,
}

enum Dialog {
    Hidden,
    AddPeriod(Form),
    EditPeriod(Form),
    DeletePeriod(NaiveDate),
}

struct Form {
    date: (String, Option<NaiveDate>),
    intensity: (String, Option<u8>),
}

// ------ ------
//    Update
// ------ ------

pub enum Msg {
    ShowAddPeriodDialog,
    ShowEditPeriodDialog(usize),
    ShowDeletePeriodDialog(NaiveDate),
    ClosePeriodDialog,

    DateChanged(String),
    IntensityChanged(String),

    SavePeriod,
    DeletePeriod(NaiveDate),
    DataEvent(data::Event),

    ChangeInterval(NaiveDate, NaiveDate),
}

pub fn update(
    msg: Msg,
    model: &mut Model,
    data_model: &data::Model,
    orders: &mut impl Orders<Msg>,
) {
    match msg {
        Msg::ShowAddPeriodDialog => {
            let local = Local::now().date().naive_local();
            model.dialog = Dialog::AddPeriod(Form {
                date: (
                    local.to_string(),
                    if data_model.period.iter().all(|p| p.date != local) {
                        Some(local)
                    } else {
                        None
                    },
                ),
                intensity: (String::new(), None),
            });
        }
        Msg::ShowEditPeriodDialog(index) => {
            let date = data_model.period[index].date;
            let intensity = data_model.period[index].intensity;
            model.dialog = Dialog::EditPeriod(Form {
                date: (date.to_string(), Some(date)),
                intensity: (intensity.to_string(), Some(intensity)),
            });
        }
        Msg::ShowDeletePeriodDialog(date) => {
            model.dialog = Dialog::DeletePeriod(date);
        }
        Msg::ClosePeriodDialog => {
            model.dialog = Dialog::Hidden;
            Url::go_and_replace(&crate::Urls::new(&model.base_url).period());
        }

        Msg::DateChanged(date) => match model.dialog {
            Dialog::AddPeriod(ref mut form) => match NaiveDate::parse_from_str(&date, "%Y-%m-%d") {
                Ok(parsed_date) => {
                    if data_model.period.iter().all(|p| p.date != parsed_date) {
                        form.date = (date, Some(parsed_date));
                    } else {
                        form.date = (date, None);
                    }
                }
                Err(_) => form.date = (date, None),
            },
            Dialog::Hidden | Dialog::EditPeriod(_) | Dialog::DeletePeriod(_) => {
                panic!();
            }
        },
        Msg::IntensityChanged(intensity) => match model.dialog {
            Dialog::AddPeriod(ref mut form) | Dialog::EditPeriod(ref mut form) => {
                match intensity.parse::<u8>() {
                    Ok(parsed_intensity) => {
                        form.intensity = (
                            intensity,
                            if parsed_intensity > 0 {
                                Some(parsed_intensity)
                            } else {
                                None
                            },
                        )
                    }
                    Err(_) => form.intensity = (intensity, None),
                }
            }
            Dialog::Hidden | Dialog::DeletePeriod(_) => {
                panic!();
            }
        },

        Msg::SavePeriod => {
            model.loading = true;
            match model.dialog {
                Dialog::AddPeriod(ref mut form) => {
                    orders.notify(data::Msg::CreatePeriod(data::Period {
                        date: form.date.1.unwrap(),
                        intensity: form.intensity.1.unwrap(),
                    }));
                }
                Dialog::EditPeriod(ref mut form) => {
                    orders.notify(data::Msg::ReplacePeriod(data::Period {
                        date: form.date.1.unwrap(),
                        intensity: form.intensity.1.unwrap(),
                    }));
                }
                Dialog::Hidden | Dialog::DeletePeriod(_) => {
                    panic!();
                }
            };
        }
        Msg::DeletePeriod(date) => {
            model.loading = true;
            orders.notify(data::Msg::DeletePeriod(date));
        }
        Msg::DataEvent(event) => {
            model.loading = false;
            match event {
                data::Event::PeriodCreatedOk
                | data::Event::PeriodReplacedOk
                | data::Event::PeriodDeletedOk => {
                    orders.skip().send_msg(Msg::ClosePeriodDialog);
                }
                _ => {}
            };
        }

        Msg::ChangeInterval(first, last) => {
            model.interval.first = first;
            model.interval.last = last;
        }
    }
}

// ------ ------
//     View
// ------ ------

pub fn view(model: &Model, data_model: &data::Model) -> Node<Msg> {
    div![
        view_period_dialog(&model.dialog, model.loading),
        common::view_fab(|_| Msg::ShowAddPeriodDialog),
        common::view_interval_buttons(&model.interval, Msg::ChangeInterval),
        common::view_diagram(
            &model.base_url,
            "period",
            &model.interval,
            &data_model
                .period
                .iter()
                .map(|p| (p.date, p.intensity as u32))
                .collect::<Vec<_>>(),
        ),
        view_table(model, data_model),
    ]
}

fn view_period_dialog(dialog: &Dialog, loading: bool) -> Node<Msg> {
    let title;
    let form;
    let date_disabled;
    match dialog {
        Dialog::AddPeriod(ref f) => {
            title = "Add period";
            form = f;
            date_disabled = false;
        }
        Dialog::EditPeriod(ref f) => {
            title = "Edit period";
            form = f;
            date_disabled = true;
        }
        Dialog::DeletePeriod(date) => {
            #[allow(clippy::clone_on_copy)]
            let date = date.clone();
            return common::view_delete_confirmation_dialog(
                "period entry",
                &ev(Ev::Click, move |_| Msg::DeletePeriod(date)),
                &ev(Ev::Click, |_| Msg::ClosePeriodDialog),
                loading,
            );
        }
        Dialog::Hidden => {
            return empty![];
        }
    }
    let save_disabled = loading || form.date.1.is_none() || form.intensity.1.is_none();
    common::view_dialog(
        "primary",
        title,
        nodes![
            div![
                C!["field"],
                label![C!["label"], "Date"],
                div![
                    C!["control"],
                    input_ev(Ev::Input, Msg::DateChanged),
                    input![
                        C!["input"],
                        C![IF![form.date.1.is_none() => "is-danger"]],
                        attrs! {
                            At::Type => "date",
                            At::Value => form.date.0,
                            At::Disabled => date_disabled.as_at_value(),
                        }
                    ],
                ]
            ],
            div![
                C!["field"],
                label![C!["label"], "Intensity"],
                div![
                    C!["control"],
                    ["1", "2", "3", "4"]
                        .iter()
                        .map(|i| {
                            button![
                                C!["button"],
                                C!["mr-2"],
                                C![IF![&form.intensity.0 == i => "is-link"]],
                                ev(Ev::Click, |_| Msg::IntensityChanged(i.to_string())),
                                i,
                            ]
                        })
                        .collect::<Vec<_>>(),
                ],
            ],
            div![
                C!["field"],
                C!["is-grouped"],
                C!["is-grouped-centered"],
                C!["mt-5"],
                div![
                    C!["control"],
                    button![
                        C!["button"],
                        C!["is-light"],
                        ev(Ev::Click, |_| Msg::ClosePeriodDialog),
                        "Cancel",
                    ]
                ],
                div![
                    C!["control"],
                    button![
                        C!["button"],
                        C!["is-primary"],
                        C![IF![loading => "is-loading"]],
                        attrs![
                            At::Disabled => save_disabled.as_at_value(),
                        ],
                        ev(Ev::Click, |_| Msg::SavePeriod),
                        "Save",
                    ]
                ],
            ],
        ],
        &ev(Ev::Click, |_| Msg::ClosePeriodDialog),
    )
}

fn view_table(model: &Model, data_model: &data::Model) -> Node<Msg> {
    div![
        C!["table-container"],
        C!["mt-4"],
        table![
            C!["table"],
            C!["is-fullwidth"],
            C!["is-hoverable"],
            C!["has-text-centered"],
            thead![tr![th!["Date"], th!["Intensity"], th![]]],
            tbody![&data_model
                .period
                .iter()
                .enumerate()
                .rev()
                .filter(|(_, p)| p.date >= model.interval.first && p.date <= model.interval.last)
                .map(|(i, p)| {
                    #[allow(clippy::clone_on_copy)]
                    let date = p.date.clone();
                    tr![
                        td![span![
                            style! {St::WhiteSpace => "nowrap" },
                            p.date.to_string(),
                        ]],
                        td![format!("{:.1}", p.intensity)],
                        td![p![
                            C!["is-flex is-flex-wrap-nowrap"],
                            a![
                                C!["icon"],
                                C!["mr-1"],
                                ev(Ev::Click, move |_| Msg::ShowEditPeriodDialog(i)),
                                i![C!["fas fa-edit"]]
                            ],
                            a![
                                C!["icon"],
                                C!["ml-1"],
                                ev(Ev::Click, move |_| Msg::ShowDeletePeriodDialog(date)),
                                i![C!["fas fa-times"]]
                            ]
                        ]]
                    ]
                })
                .collect::<Vec<_>>()],
        ]
    ]
}