export type User = {
    id: string;
    firstName: string;
    lastName: string;
    email: string;
    password?: string;
    role: string;
};

export const ROLES = ["user", "admin"];

export type UserJson = {
    _id: string;
    first_name: string;
    last_name: string;
    email: string;
    role: string;
};

export type UserCreateJson = {
    _id: string;
    first_name: string;
    last_name: string;
    email: string;
    password: string;
    role: string;
};

export type UserUpdateJson = {
    first_name: string;
    last_name: string;
    email: string;
    role: string;
};

function deserializeUser(user: UserJson): User {
    return {
        id: user._id,
        email: user.email,
        firstName: user.first_name,
        lastName: user.last_name,
        role: user.role
    }
}

function serializeUserCreate(user: User): UserCreateJson {
    return {
        _id: user.id,
        first_name: user.firstName,
        last_name: user.lastName,
        email: user.email,
        password: user.password!,
        role: user.role,
    }
}

function serializeUserUpdate(user: User): UserUpdateJson {
    return {
        first_name: user.firstName,
        last_name: user.lastName,
        email: user.email,
        role: user.role,
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
    const body = serializeUserCreate(user);
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
    const body = serializeUserUpdate(user);
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