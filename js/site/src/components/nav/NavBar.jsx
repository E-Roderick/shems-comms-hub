import { For } from "solid-js";
import { A } from "@solidjs/router";
import "./Nav.css";

function NavLink(props) {
    return (
        <A class="navlink" href={props.href}>{props.text}</A>
    )
}

export default function NavBar() {
    const links = [
        { href: "/devices", text: "Devices" },
        { href: "/alarms", text: "Alarms" },
        { href: "/logs", text: "Logs" },
    ];

    return (
        <nav class="navbar">
            <ul>
                <For each={links}>
                    {link => <NavLink {...link} />}
                </For>
            </ul>
        </nav>
    )
}
