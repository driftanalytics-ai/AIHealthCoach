# Generated by Django 4.2.14 on 2024-11-08 23:38

import analytics.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('model_name', models.CharField(default='GPT-4o', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Edge',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('end', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_agent', to='analytics.agent')),
                ('start', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_agent', to='analytics.agent')),
            ],
        ),
        migrations.CreateModel(
            name='Graph',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('hash', models.CharField(max_length=64, unique=True)),
                ('edges', models.ManyToManyField(to='analytics.edge')),
                ('nodes', models.ManyToManyField(to='analytics.agent')),
            ],
        ),
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('average', models.FloatField(default=0)),
                ('min_val', models.FloatField(default=10000000)),
                ('max_val', models.FloatField(default=0)),
                ('standard_deviation', models.FloatField(default=0)),
                ('variance', models.FloatField(default=0)),
                ('count', models.IntegerField(default=0)),
                ('sum_val', models.FloatField(default=0)),
                ('sum_squares_val', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('query_text', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('graph', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='analytics.graph')),
            ],
        ),
        migrations.CreateModel(
            name='AgentQuery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_usage', models.IntegerField()),
                ('response', models.TextField(default='DEFAULT_RESPONSE')),
                ('startTimestamp', models.DateTimeField()),
                ('endTimestamp', models.DateTimeField()),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics.agent')),
                ('queryId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics.query')),
            ],
        ),
        migrations.AddField(
            model_name='agent',
            name='runtime_stats',
            field=models.ForeignKey(default=analytics.models.get_default_stats_id, on_delete=django.db.models.deletion.CASCADE, related_name='runtime_agent', to='analytics.stats'),
        ),
        migrations.AddField(
            model_name='agent',
            name='token_usage_stats',
            field=models.ForeignKey(default=analytics.models.get_default_stats_id, on_delete=django.db.models.deletion.CASCADE, related_name='token_usage_agent', to='analytics.stats'),
        ),
    ]