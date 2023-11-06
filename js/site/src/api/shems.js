import { create } from "xmlbuilder2";
import { currentTime } from "../utils/time";
import { SHEMS_API_ADDR, SHEMS_API_PORT } from "../utils/env_var.js"

const SHEMS_ENDPOINT_NOTIFY =
	`http://${SHEMS_API_ADDR}:${SHEMS_API_PORT}/shem/ntfy/`;

function createControlMessage(
	deviceId,
	control,
	value,
	isDefault,
	created,
	start,
	duration
) {
	// Root object name
	const controlType = isDefault ? "DefaultDERControl" : "DERControl";

	// Attributes
	const href = "null";
	const replyTo = "null";
	const responses = "00";

	// XML body content
	const preamble = {
		mRID: deviceId,
		description: "A web-created control.",
		creationTime: String(currentTime())
	};
	const controlBase = {
		[control]: value,
	};
	const timing = isDefault ? {} : {
		EventStatus: {
			currentStatus: "0",
			dateTime: String(created),
			potentiallySuperceded: "false"
		},
		interval: {
			duration: String(duration),
			start: String(start)
		}
	};

	// Construct XML
	const obj = {
		[controlType]: {
			'@href': href,
			'@replyTo': replyTo,
			'@responsesRequired': responses,
			// NOTE 'responsesRequired' is the incorrect label. It should be
			// 'responseRequired'.
			...preamble,
			...timing,
			DERControlBase: controlBase
		}
	}
	const doc = create(obj);
	const xml = doc.end();

	// Return version without version data
	const VERSION = '<?xml version="1.0"?>'
	return xml.replace(VERSION, '');
};

function sendShems(endpoint, method, data) {
	return fetch(endpoint, {
		method: method,
		body: data,
		headers: {
			"Content-type": "application/sep+xml",
			"Access-Control-Allow-Origin": "*",
		}
	});
}

export {
	SHEMS_ENDPOINT_NOTIFY,
	createControlMessage,
	sendShems,
};
