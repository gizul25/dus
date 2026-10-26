import { createColumnHelper, renderComponent } from "@tanstack/svelte-table";
import type { DataTableFeatures } from "./data-table-features.js";
import DataTableCheckbox from "./DataTableCheckbox.svelte";
import DataTableEmailButton from "./DataTableEmailButton.svelte";
import DataTableActions from "./DataTableActions.svelte";

export type User = {
    id: string;
    firstName: string;
    lastName: string;
    email: string;
};

const columnHelper = createColumnHelper<DataTableFeatures, User>();

export const columns = columnHelper.columns([
    columnHelper.display({
        id: "select",
        header: ({ table }) =>
            renderComponent(DataTableCheckbox, {
                checked: table.getIsAllPageRowsSelected(),
                indeterminate:
                    table.getIsSomePageRowsSelected() &&
                    !table.getIsAllPageRowsSelected(),
                onCheckedChange: (value: boolean) =>
                    table.toggleAllPageRowsSelected(!!value),
                "aria-label": "Select all",
            }),
        cell: ({ row }) =>
            renderComponent(DataTableCheckbox, {
                checked: row.getIsSelected(),
                onCheckedChange: (value: boolean) => row.toggleSelected(!!value),
                "aria-label": "Select row",
            }),
        enableSorting: false,
        enableHiding: false,
        size: 24
    }),
    columnHelper.accessor("firstName", {
        header: "First name",
    }),
    columnHelper.accessor("lastName", {
        header: "Last name",
    }),
    columnHelper.accessor("email", {
        header: ({ column }) =>
            renderComponent(DataTableEmailButton, {
                onclick: column.getToggleSortingHandler(),
            }),
    }),
    columnHelper.display({
        id: "actions",
        size: 50,
        cell: ({ row }) => {
            return renderComponent(DataTableActions, { id: row.original.id });
        },
    }),
]);