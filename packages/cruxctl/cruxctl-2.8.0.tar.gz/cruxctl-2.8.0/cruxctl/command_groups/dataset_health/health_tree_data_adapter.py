import datetime
from collections import defaultdict

from google.cloud.bigquery.table import RowIterator
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from cruxctl.command_groups.dataset_health.models.dataset_health_branch import (
    DatasetHealthBranch,
)


class HealthTreeDataAdapter:
    def bigquery_to_health_tree_by_dataset(self, bq_row_iterator: RowIterator) -> Tree:
        tree = self._create_base_tree()

        for bq_row in bq_row_iterator:
            self._append_dataset_health_branch(
                tree,
                bq_row.get("dataset_id"),
                bq_row.get("aggregated_status"),
                bq_row.get("processing_status"),
                bq_row.get("delivery_deadline"),
                bq_row.get("dispatch_statuses"),
                bq_row.get("subscription_ids"),
                bq_row.get("subscribers"),
            )

        return tree

    def _create_base_tree(self) -> Tree:
        return Tree("", guide_style="bold bright_blue", hide_root=True)

    def _append_dataset_health_branch(
        self,
        tree: Tree,
        dataset_id: str,
        aggregated_status: str,
        processing_status: str,
        delivery_deadline: datetime,
        dispatch_statuses: list[str],
        subscription_ids: list[str],
        subscribers: list[str] = None,
    ):
        aggregated_health_branch = tree.add(
            Panel(
                self._get_styled_status(
                    aggregated_status,
                    f" | Dataset ID: {dataset_id} | Deadline: {delivery_deadline} ",
                ),
                title="Dataset Health",
                title_align="left",
                expand=False,
            )
        )

        processing_health_branch = aggregated_health_branch.add(
            Panel(
                self._get_styled_status(processing_status),
                title="Processing Health",
                title_align="left",
                expand=False,
            )
        )

        if subscribers:
            self._append_health_leaves(
                processing_health_branch,
                dispatch_statuses,
                subscription_ids,
                subscribers,
            )
        else:
            self._append_health_leaves_no_subscribers(
                processing_health_branch, dispatch_statuses, subscription_ids
            )

    def _append_health_leaves(
        self,
        branch: Tree,
        dispatch_statuses: list[str],
        subscription_ids: list[str],
        subscribers: list[str],
    ):
        for dispatch_status, subscription_id, subscriber in zip(
            dispatch_statuses, subscription_ids, subscribers
        ):
            styled_status = self._get_styled_status(
                dispatch_status,
                f" | Subscriber {subscriber} | Subscription ID: {subscription_id}",
            )

            leaf = Panel(
                styled_status,
                title="Dispatch Health",
                title_align="left",
                expand=False,
            )

            branch.add(leaf)

    def _append_health_leaves_no_subscribers(
        self, branch: Tree, dispatch_statuses: list[str], subscription_ids: list[str]
    ):
        for dispatch_status, subscription_id in zip(
            dispatch_statuses, subscription_ids
        ):
            styled_status = self._get_styled_status(
                dispatch_status, f" | Subscription ID: {subscription_id}"
            )

            leaf = Panel(
                styled_status,
                title="Dispatch Health",
                title_align="left",
                expand=False,
            )

            branch.add(leaf)

    def _get_styled_status(self, status: str, extra_text: str = None) -> Text:
        if status == "healthy":
            style = "bold green"
            icon = "🟢"
        elif status == "delivered_late":
            style = "bold gold1"
            icon = "🟡"
        else:
            style = "bold red"
            icon = "🔴"

        title = f"{icon} {status.title().replace('_', ' ')}"

        text = Text(title, style=style)

        if extra_text:
            text += Text(extra_text, style="grey50")

        return text

    def bigquery_to_health_tree_by_subscriber(
        self, bq_row_iterator: RowIterator
    ) -> Tree:
        tree = self._create_base_tree()

        subscriber_health_branch_multimap = defaultdict(list[DatasetHealthBranch])

        for bq_row in bq_row_iterator:
            subscriber_id = bq_row.get("subscriber_id")

            health_branch = DatasetHealthBranch(**bq_row)

            subscriber_health_branch_multimap[subscriber_id].append(health_branch)

        for subscriber_id, health_branches in subscriber_health_branch_multimap.items():
            subscriber_health_branch = tree.add(
                Panel(
                    f"{subscriber_id}",
                    title="Subscriber",
                    title_align="left",
                    expand=False,
                )
            )

            for health_branch in health_branches:
                self._append_dataset_health_branch(
                    subscriber_health_branch,
                    health_branch.dataset_id,
                    health_branch.aggregated_status,
                    health_branch.processing_status,
                    health_branch.delivery_deadline,
                    health_branch.dispatch_statuses,
                    health_branch.subscription_ids,
                )

        return tree
