import { A } from "@solidjs/router";
import NavBar from "./nav/NavBar";
import "./SideBar.css";

export default function SideBar() {
    return (
        <aside class="sidebar">
            <A id="home-btn" href="/">SHEMS</A>
            <div class="h-div" />
            <NavBar />
        </aside>
    );
}
