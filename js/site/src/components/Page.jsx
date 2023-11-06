import { Title } from "solid-start";
import "./Page.css";

export default function Page(props) {
    return (
        <main>
            <Title>{props.title}</Title>
            <div>
                <h1>{props.heading}</h1>
                <article class="main">
                    {props.children}
                </article>
            </div>
        </main>
    );
}
