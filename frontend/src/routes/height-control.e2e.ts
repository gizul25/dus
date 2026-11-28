import { expect, test } from '@playwright/test';

type DeskProfile = {
	seated_max_height_cm: number;
	standing_min_height_cm: number;
};

type HeightReading = {
	height_cm: number;
	recorded_at: string;
};

type DeskStatus = {
	height_cm: number | null;
	last_reading_at: string | null;
};

const baseURL = (process.env.PLAYWRIGHT_BASE_URL ?? 'http://nginx:8080').replace(/\/$/, '');
const deskApi = `${baseURL}/api/desk`;

test('a height reading updates the desk status and measurement history', async ({ request }) => {
	const profileResponse = await request.get(`${deskApi}/profile`);
	expect(profileResponse.status()).toBe(200);
	const profile: DeskProfile = await profileResponse.json();

	const historyResponse = await request.get(`${deskApi}/measurements?limit=1`);
	expect(historyResponse.status()).toBe(200);
	const history: HeightReading[] = await historyResponse.json();
	const latestTimestamp = history[0] ? Date.parse(history[0].recorded_at) : 0;
	const recordedAt = new Date(Math.max(Date.now(), latestTimestamp) + 1000);
	const height = (profile.seated_max_height_cm + profile.standing_min_height_cm) / 2;

	const readingResponse = await request.post(`${deskApi}/readings`, {
		data: {
			height_cm: height,
			recorded_at: recordedAt.toISOString()
		}
	});

	expect(readingResponse.status()).toBe(200);
	const readingStatus: DeskStatus = await readingResponse.json();
	expect(readingStatus.height_cm).toBe(height);
	if (readingStatus.last_reading_at === null) {
		throw new Error('The desk status did not include the recorded reading timestamp.');
	}
	expect(Date.parse(readingStatus.last_reading_at)).toBe(recordedAt.getTime());

	const statusResponse = await request.get(`${deskApi}/status`);
	expect(statusResponse.status()).toBe(200);
	const status: DeskStatus = await statusResponse.json();
	expect(status.height_cm).toBe(height);

	const latestResponse = await request.get(`${deskApi}/measurements?limit=1`);
	expect(latestResponse.status()).toBe(200);
	const latest: HeightReading[] = await latestResponse.json();
	expect(latest).toHaveLength(1);
	expect(latest[0].height_cm).toBe(height);
	expect(Date.parse(latest[0].recorded_at)).toBe(recordedAt.getTime());
});

test('an invalid height is rejected without changing the latest measurement', async ({
	request
}) => {
	const beforeResponse = await request.get(`${deskApi}/measurements?limit=1`);
	expect(beforeResponse.status()).toBe(200);
	const before: HeightReading[] = await beforeResponse.json();

	const invalidResponse = await request.post(`${deskApi}/readings`, {
		data: { height_cm: 0 }
	});
	expect(invalidResponse.status()).toBe(422);

	const afterResponse = await request.get(`${deskApi}/measurements?limit=1`);
	expect(afterResponse.status()).toBe(200);
	const after: HeightReading[] = await afterResponse.json();
	expect(after).toEqual(before);
});
