import { For, Show, Suspense, createEffect, createResource } from "solid-js";
import { fetchLogs } from "~/api/fetching";
import Page from "~/components/Page";
import "./logs.css"

export default function Logs() {
    const [logs] = createResource(fetchLogs);

    createEffect(() => {
        !logs.loading && console.log(logs());
    });

    return (
        <Page title={"System Logs"} heading={"System Logs"} >
            <article class="log-container">
                <Suspense fallback={<p>Loading logs...</p>}>
                    <For each={logs()} >
                        {(logLine) => <pre>{logLine}</pre>}
                    </For>
                </Suspense>
            </article>
        </Page>
    );
}
