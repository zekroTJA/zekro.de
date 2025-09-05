#!/usr/bin/env python3

import yaml


# WEEKDAYS = (
#     ("mon", "Montag"),
#     ("tue", "Dienstag"),
#     ("wed", "Mittwoch"),
#     ("thu", "Donnerstag"),
#     ("fri", "Freitag"),
#     ("sat", "Samstag"),
#     ("sun", "Sontag"),
# )

WEEKDAYS = {
    "mon": "Montag",
    "tue": "Dienstag",
    "wed": "Mittwoch",
    "thu": "Donnerstag",
    "fri": "Freitag",
    "sat": "Samstag",
    "sun": "Sonntag",
}


def print_indent(level, content):
    if level <= 0:
        print(content)
    else:
        print(f"{'  ' * level}{content}")


def get_project_at(projects, wdid, time_slot):
    for project in projects:
        if wdid in project["wdays"] and time_slot == project["at"]:
            return project
    return None


def main():
    with open(0, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    projects = data["projects"]

    time_slots = sorted(set(v["at"] for v in projects))

    schedule = {}
    for wdid, _ in WEEKDAYS.items():
        entries = []
        for time_slot in time_slots:
            if project := get_project_at(projects, wdid, time_slot):
                entries.append(project)
            else:
                entries.append(None)
        schedule[wdid] = entries

    print_indent(0, "<table>")

    print_indent(1, "<thead>")
    print_indent(2, "<tr>")
    print_indent(3, "<th>Wochentag</th>")
    for time_slot in time_slots:
        print_indent(3, f"<th>{time_slot}</th>")
    print_indent(2, "</tr>")
    print_indent(1, "</thead>")

    print_indent(1, "<tbody>")
    for wdid, entries in schedule.items():
        print_indent(2, "<tr>")
        print_indent(3, f"<th>{WEEKDAYS[wdid]}</th>")
        for entry in entries:
            if entry:
                print_indent(3, f'<td class="{entry["id"]}">')
                print_indent(4, f"<span>{entry['name']}</span>")
                if sub := entry.get("sub"):
                    print_indent(4, f'<span class="sub">{sub}</span>')
                print_indent(3, "</td>")
            else:
                print_indent(3, "<td></td>")
        print_indent(2, "</tr>")
    print_indent(1, "</tbody>")

    print_indent(0, "</table>")


if __name__ == "__main__":
    main()
