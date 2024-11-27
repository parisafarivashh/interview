from django.core.management.base import BaseCommand

from report_flow.models import set_pipline_base_mode
from zibal_project.utils import create_connection_db


class Command(BaseCommand):
    help = 'Run aggregation and save results to a transaction_summary'

    def handle(self, *args, **options):
        modes = ['daily', 'weekly', 'monthly']
        db = create_connection_db()
        db.transaction_summary.drop()

        for mode in modes:
            pipeline = self._get_pipline(mode)
            self._set_data_in_collection(pipeline, mode)

            pipeline = self._get_pipline_group_by_merchant_id(mode)
            self._set_data_in_collection(pipeline, mode)


        self.stdout.write(self.style.SUCCESS('Successfully aggregated and saved data'))

    @staticmethod
    def _set_data_in_collection(pipeline: list, mode: str) -> None:
        db = create_connection_db()

        pipeline.append({
            '$addFields': {
                'type_mode': mode, # daily, weekly, monthly
            }
        })
        results = list(db.transaction.aggregate(pipeline))
        db.transaction_summary.insert_many(results)

    @staticmethod
    def _get_pipline_group_by_merchant_id(mode: str) -> list:
        pipeline = []
        set_pipline_base_mode(pipeline, mode, ['amount', 'merchantId'])

        pipeline.append({
            '$group': {
                '_id': {
                    'value_mode': f'${mode}',
                    'merchantId': '$merchantId'
                },
                'count': {'$sum': 1},
                'amount': {'$sum': '$amount'},
            }
        })
        pipeline.append({
            '$project': {
                '_id': '$_id',
                'count': 1,
                'amount': 1,
            }
        })
        return pipeline


    @staticmethod
    def _get_pipline(mode: str) -> list:
        pipeline = []
        set_pipline_base_mode(pipeline, mode, ['amount'])

        pipeline.append({
            '$group': {
                '_id': {
                    'value_mode': f'${mode}',
                },
                'count': {'$sum': 1},
                'amount': {'$sum': '$amount'},
            }
        })
        pipeline.append({
            '$project': {
                '_id': '$_id',
                'count': 1,
                'amount': 1,
            }
        })
        return pipeline


