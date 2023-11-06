import { A } from "@solidjs/router";
import { createResource } from "solid-js";
import { fetchAlarms, fetchDevices } from "~/api/fetching";
import Page from "~/components/Page";
import { deviceURL } from "~/paths";
import { timeStampToDate } from "~/utils/time";
import "./alarms.css"
import "./devices/devices.css"

const AlarmListing = (props) => {
    const {
        dev_id: deviceId,
        description,
        code,
        value,
        reading_time: read
    } = props;

    const localeRead = timeStampToDate(read).toLocaleString();

    return (
        <li class="card alarm-listing">
            <div class="alarm-device-details">
                <A href={deviceURL(deviceId)}><h3>{description}</h3></A>
                <p class="device-mrid">{deviceId}</p>
            </div>
            <div class="alarm-contents">
                <p><span class="alarm-time">{localeRead}</span></p>
                <p>
                    <span class="device-setting-code">
                        {code}
                    </span> alarmed at value {value}
                </p>
            </div>
        </li>
    );
}

const AlarmList = ({ alarms, devices }) => {
    const data = alarms.map(alarm => ({
        ...alarm,
        ...devices.find(device => device.dev_id === alarm.dev_id)
    }));

    return (
        <ul class="alarm-list">
            <For each={data} >
                {(alarm) => <AlarmListing {...alarm} />}
            </For>
        </ul>
    );
}

export default function Alarms() {
    const [alarmData] = createResource(fetchAlarms);
    const [deviceData] = createResource(fetchDevices);

    return (
        <Page title={"SHEMS Alarms"} heading={"Device Alarms"} >
            <Show
                when={!alarmData.loading && !deviceData.loading}
                fallback={<p>Loading alarms...</p>}
            >
                <AlarmList alarms={alarmData()} devices={deviceData()} />
            </Show>
        </Page>
    );
}
