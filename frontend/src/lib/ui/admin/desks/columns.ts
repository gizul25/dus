import { createColumnHelper, renderComponent } from "@tanstack/svelte-table";
import type { DataTableFeatures } from "#lib/ui/admin/table/data-table-features.js";
import DataTableCheckbox from "./DataTableCheckbox.svelte";
import DataTableActions from "./DataTableActions.svelte";

export type Desk = {
    id: string;
    name: string;
};

const columnHelper = createColumnHelper<DataTableFeatures, Desk>();

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
    columnHelper.accessor("id", {
        header: "Desk ID",
    }),
    columnHelper.accessor("name", {
        header: "Name",
    }),
    columnHelper.display({
        id: "actions",
        size: 50,
        cell: ({ row }) => {
            return renderComponent(DataTableActions, { id: row.original.id });
        },
    }),
]);