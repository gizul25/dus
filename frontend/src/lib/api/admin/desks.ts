export type Desk = {
    id: string;
    name: string;
};

export type DeskJson = {
    _id: string;
    name: string;
};

function deserializeDesk(desk: DeskJson): Desk {
    return {
        id: desk._id,
        name: desk.name,
    }
}

function serializeDesk(desk: Desk): DeskJson {
    return {
        _id: desk.id,
        name: desk.name,
    }
}

export async function getDesks(): Promise<Desk[]> {
    const res = await fetch("/api/admin/desks/");
    const json = await res.json();
    const desks = json.map((d: DeskJson) => deserializeDesk(d));
    return desks;
}

export async function getDesk(id: string): Promise<Desk> {
    const res = await fetch(`/api/admin/desks/${id}`);
    const json = await res.json();
    const desk = deserializeDesk(json);
    return desk;
}

export async function createDesk(desk: Desk): Promise<string> {
    const body = serializeDesk(desk);
    const res = await fetch(
        `/api/admin/desks/`,
        {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        }
    );
    const json = await res.json();
    return json;
}

export async function updateDesk(desk: Desk): Promise<Desk> {
    const body = serializeDesk(desk);
    const res = await fetch(
        `/api/admin/desks/${desk.id}`,
        {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        }
    );
    const json = await res.json();
    const resDesk = deserializeDesk(json);
    return resDesk;
}

export async function deleteDesk(id: string): Promise<void> {
    await fetch(
        `/api/admin/desks/${id}`,
        {
            method: 'DELETE',
        }
    );
}