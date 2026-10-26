import { createColumnHelper, renderSnippet, renderComponent } from "@tanstack/svelte-table";
import { createRawSnippet } from "svelte";
import type { DataTableFeatures } from "./data-table-features.js";
import DataTableCheckbox from "./DataTableCheckbox.svelte";
import DataTableEmailButton from "./DataTableEmailButton.svelte";
import DataTableActions from "./DataTableActions.svelte";

// This type is used to define the shape of our data.
// You can use a Zod schema here if you want.
export type Payment = {
    id: string;
    amount: number;
    status: "pending" | "processing" | "success" | "failed";
    email: string;
};

// Use `accessor` for data columns and `display` for columns without one.
const columnHelper = createColumnHelper<DataTableFeatures, Payment>();

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
    }),
    columnHelper.accessor("status", {
        header: "Status",
    }),
    columnHelper.accessor("email", {
        header: ({ column }) =>
            renderComponent(DataTableEmailButton, {
                onclick: column.getToggleSortingHandler(),
            }),
    }),
    columnHelper.accessor("amount", {
        header: () => {
            const amountHeaderSnippet = createRawSnippet(() => ({
                render: () => `<div class="text-end">Amount</div>`,
            }));
            return renderSnippet(amountHeaderSnippet);
        },
        cell: ({ row }) => {
            const formatter = new Intl.NumberFormat("en-US", {
                style: "currency",
                currency: "USD",
            });

            const amountCellSnippet = createRawSnippet<[{ amount: number }]>(
                (getAmount) => {
                    const { amount } = getAmount();
                    const formatted = formatter.format(amount);
                    return {
                        render: () =>
                            `<div class="text-end font-medium">${formatted}</div>`,
                    };
                }
            );

            return renderSnippet(amountCellSnippet, {
                amount: row.original.amount,
            });
        },
    }),
    columnHelper.display({
        id: "actions",
        cell: ({ row }) => {
            return renderComponent(DataTableActions, { id: row.original.id });
        },
    }),
]);