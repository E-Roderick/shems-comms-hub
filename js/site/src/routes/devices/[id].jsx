import { For, Show, createEffect, createResource, createSignal } from "solid-js";
import { useParams } from "@solidjs/router";
import { createStore } from "solid-js/store";

import {
    fetchDevice,
    fetchDeviceStatus,
    fetchDeviceSettings
} from "~/api/fetching";
import { createControlMessage } from "~/api/shems";
import { SHEMS_ENDPOINT_NOTIFY, sendShems } from "~/api/shems";
import Page from "~/components/Page";
import { currentTime, datetimeStringToTimestamp } from "~/utils/time";
import { timeStampToDate } from "../../utils/time";

const WAIT_TIME = 300; // ms

const DeviceInfo = ({
    description,
    dev_id: deviceId,
    last_ip: lastIp,
    reading_time: readTime
}) => {
    const time = new Date(readTime * 1000);

    return (
        <section class="card device-info">
            <div class="device-identity">
                <h2>{description}:</h2>
                <p class="device-mrid">{deviceId}</p>
            </div>
            <div class="device-contact">
                <p>Last known at address '{lastIp}'</p>
                <p>Updated: {time.toLocaleString()}</p>
            </div>
        </section>
    )
};

const DeviceStatus = ({connect_status: connected, charge_state: charge}) => {
    const connectStatus = connected ? "connected" : "disconnected";
    const chargeLevel = charge ? `at ${parseFloat(charge) * 100}%`: "not known";

    const chargeToColour = charge => {
        let colour = "gray";
        charge = parseFloat(charge);
        if (isNaN(charge)) {
            return colour;
        }

        if (charge > 0.6) colour = "green";
        else if (charge > 0.35) colour = "goldenrod";
        else colour = "red";
        return colour;
    };

    return (
        <section class="card device-status">
            <h3>Device Status</h3>
            <div class="device-status-content">
                <p>Device {connectStatus}.</p>
                <p>Device charge&nbsp;
                    <span style={{ color: chargeToColour(charge) }}>
                        {chargeLevel}
                    </span>.
                </p>
            </div>
        </section>
    )
};

const DeviceSettingsInput = ({ deviceId, refreshData }) => {
    const [form, setForm] = createStore({
        code: "",
        value: "",
        default: true,
        start: 0,
        duration: 0
    });

    // Return a function that takes an event and updates the form
    const fieldUpdater = (field) => {
        return (event) => {
            const elem = event.currentTarget;
            const newValue = elem.type === "checkbox" ?
                !!elem.checked :
                elem.value;

            setForm({ [field]: newValue });
        }
    }

    const handleSubmit = (event) => {
        event.preventDefault();
        const start = datetimeStringToTimestamp(form.start);
        const duration = parseFloat(form.duration);

        // Notify the controller of the new control
        const controlMsg = createControlMessage(
            deviceId,
            form.code,
            form.value,
            form.default,
            currentTime(),
            start, duration
        );
        sendShems(SHEMS_ENDPOINT_NOTIFY, "POST", controlMsg);

        // Refresh the data after some time
        setTimeout(refreshData, WAIT_TIME);

        // Reset the form
        document.getElementById("device-control-form").reset();
    }

    const disableClass = isDisabled => {
        return isDisabled ? "disabled" : "";
    }

    return (
        <section class="card device-update-settings">
            <form onSubmit={handleSubmit} id="device-control-form">
                <h3>Update Device Controls</h3>
                <div className="device-settings-inputs">
                    <div class="single-input">
                        <label for="device-setting-code">
                            Control Code
                        </label>
                        <input
                            id="device-setting-code"
                            class="textual-input"
                            name="code"
                            type="text"
                            placeholder="opCode"
                            value={form.code}
                            onChange={fieldUpdater("code")}
                            required
                        />
                    </div>
                    <div class="single-input">
                        <label for="device-setting-value">
                            Value
                        </label>
                        <input
                            id="device-setting-value"
                            class="textual-input"
                            name="value"
                            type="text"
                            value={form.value}
                            onChange={fieldUpdater("value")}
                            required
                        />
                    </div>
                    <div id="is-default-input" class="single-input">
                        <label for="device-setting-default">
                            Is Default?
                        </label>
                        <input
                            id="device-setting-default"
                            name="is-default"
                            type="checkbox"
                            checked={form.default}
                            value={form.default}
                            onChange={fieldUpdater("default")}
                        />
                    </div>
                    <div class={"single-input " + disableClass(form.default)} >
                        <label for="device-setting-start">
                            Starting Time
                        </label>
                        <input
                            id="device-setting-start"
                            class="textual-input"
                            name="start"
                            type="datetime-local"
                            value={form.start}
                            onChange={fieldUpdater("start")}
                            disabled={form.default}
                            required={!form.default}
                        />
                    </div>
                    <div class={"single-input " + disableClass(form.default)} >
                        <label for="device-setting-duration">
                            Duration (seconds)
                        </label>
                        <input
                            id="device-setting-duration"
                            class="textual-input"
                            name="duration"
                            type="number"
                            value={form.duration}
                            onChange={fieldUpdater("duration")}
                            disabled={form.default}
                            required={!form.default}
                        />
                    </div>
                </div>
                <button id="setting-update-btn" type="submit">
                    Update
                </button>
            </form>
        </section>
    );
}

const DeviceSettingsListing = (props) => {
    // Default values
    const { code, value, is_default: isDefault } = props;
    // Optional values
    const {
        creation_time: created,
        start_time: start,
        duration,
        finish_time: finish
    } = props;

    const localeCreated = timeStampToDate(created).toLocaleString();
    const localeStart = timeStampToDate(start).toLocaleString();
    const localeFinish = timeStampToDate(finish).toLocaleString();
    console.log(props, code, value);

    return (
        <li className="device-setting-listing">
            <p><span className="device-setting-code">{code}</span>: {value}</p>
            <Show when={!isDefault} >
                <div class="setting-time-info">
                    <p class="setting-active-time">
                        Active {localeStart} to {localeFinish}
                    </p>
                    <p class="setting-creation-time">Created: {localeCreated}</p>
                </div>
            </Show>
        </li>
    );
};

const DeviceSettingsView = ({ settings, title }) => {
    return (
        <section class="card device-settings-view">
            <h3>{title}</h3>
            <ul class="device-settings-list">
                <For each={settings()} >
                    {(setting) => <DeviceSettingsListing {...setting} />}
                </For>
            </ul>
        </section>
    )
};

const DeviceSettings = ({ deviceId, settings, refreshData }) => {
    const [defaultSettings, setDefaultSettings] = createSignal([]);
    const [nonDefaultSettings, setNonDefaultSettings] = createSignal([]);

    createEffect(() => {
        !settings.loading && setDefaultSettings(settings.latest[0]);
        !settings.loading && setNonDefaultSettings(settings.latest[1]);
    });

    return (
        <article class="device-settings">
            <DeviceSettingsInput deviceId={deviceId} refreshData={refreshData}/>
            <Show when={defaultSettings().length}>
                <DeviceSettingsView
                    settings={defaultSettings}
                    title={"Default Controls"}
                />
            </Show>
            <Show when={nonDefaultSettings().length}>
                <DeviceSettingsView
                    settings={nonDefaultSettings}
                    title={"Active Controls"}
                />
            </Show>
        </article>
    )
}

export default function Device() {
    const params = useParams();
    const deviceId = params.id;
    const [deviceData] = createResource(deviceId, fetchDevice);
    const [statusData] = createResource(deviceId, fetchDeviceStatus);
    const [settingsData, { refetch: refetchSettings } ] = createResource(
        deviceId,
        fetchDeviceSettings
    );

    return (
        <Page title={"SHEMS Device"} heading={"SHEMS Device"} >
            <div class="device-content">
                <Show when={!deviceData.loading && !statusData.loading} >
                    <DeviceInfo {...deviceData()} {...statusData()}/>
                    <DeviceStatus {...statusData()} />
                    <DeviceSettings
                        deviceId={deviceId}
                        settings={settingsData}
                        refreshData={refetchSettings}
                    />
                </Show>
            </div>
        </Page>
    );
}