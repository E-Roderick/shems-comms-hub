import { For, Show, createEffect, createResource } from "solid-js";
import { A } from "@solidjs/router";

import Page from "~/components/Page";
import { fetchDevices } from "~/api/fetching";
import { deviceURL } from "~/paths";
import "./devices.css";

const DeviceListing = (props) => {
    const { dev_id: deviceId, description } = props.data;
    return (
        <li class="card device-listing">
            <A href={deviceURL(deviceId)}><h3>{description}</h3></A>
            <p class="device-mrid">{deviceId}</p>
        </li>
    );
}

const DeviceList = ({ devices }) => {
    return (
        <ul>
            <For each={devices} >
                {(device) => <DeviceListing data={device} />}
            </For>
        </ul>
    );
}

export default function Devices() {
    const [data] = createResource(fetchDevices);
    console.log(data.loading, data.error);

    createEffect(() => {
        !data.loading && console.log(data());
    });

    return (
        <Page title={"SHEMS Devices"} heading={"Device List"} >
            <Show when={!data.loading} fallback={<p>Loading devices...</p>} >
                <DeviceList devices={data()} />
            </Show>
        </Page>

    );
}
