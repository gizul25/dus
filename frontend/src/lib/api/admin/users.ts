export type User = {
    id: string;
    firstName: string;
    lastName: string;
    email: string;
};

export type UserJson = {
    _id: string;
    first_name: string;
    last_name: string;
    email: string;
};

function deserializeUser(user: UserJson): User {
    return {
        id: user._id,
        email: user.email,
        firstName: user.first_name,
        lastName: user.last_name
    }
}

function serializeUser(user: User): UserJson {
    return {
        _id: user.id,
        email: user.email,
        first_name: user.firstName,
        last_name: user.lastName
    }
}

export async function getUsers(): Promise<User[]> {
    const res = await fetch("/api/admin/users/");
    const json = await res.json();
    const users = json.map((u: UserJson) => deserializeUser(u));
    return users;
}

export async function getUser(id: string): Promise<User> {
    const res = await fetch(`/api/admin/users/${id}`);
    const json = await res.json();
    const user = deserializeUser(json);
    return user;
}

export async function createUser(user: User): Promise<string> {
    const body = serializeUser(user);
    const res = await fetch(
        `/api/admin/users/`,
        {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        }
    );
    const json = await res.json();
    return json;
}

export async function updateUser(user: User): Promise<User> {
    const body = serializeUser(user);
    const res = await fetch(
        `/api/admin/users/${user.id}`,
        {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        }
    );
    const json = await res.json();
    const resUser = deserializeUser(json);
    return resUser;
}

export async function deleteUser(id: string): Promise<void> {
    await fetch(
        `/api/admin/users/${id}`,
        {
            method: 'DELETE',
        }
    );
}