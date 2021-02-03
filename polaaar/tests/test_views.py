from django.urls import reverse
from django.test import TestCase


class ProjectMetadataDetailTest(TestCase):
    """Ensure ProjectMetadata object returns correct related objects."""
    fixtures = ['polaaar/project_metadata_detail.json']
    maxDiff = None

    def setUp(self):
        project_metadata_detail_url = reverse('polaaar:project_metadata_detail', args=[1, ])
        self.response = self.client.get(project_metadata_detail_url)
        self.context = self.response.context
        return self

    def test_return_404(self):
        """
        Ensure 404 is returned if ProjectMetadata objects is not found.
        """
        project_metadata_detail_url = reverse('polaaar:project_metadata_detail', args=[5, ])
        response = self.client.get(project_metadata_detail_url)
        self.assertEqual(response.status_code, 404)

    def test_event_count(self):
        """
        Ensure that the event_count has the correct value.
        """
        self.assertEqual(self.context.get('event_count'), 2)

    def test_event_per_year(self):
        """
        Ensure that the event per year is correctly aggregated
        """
        self.assertQuerysetEqual(
            self.context.get('event_per_year'), ["{'collection_year': 2012, 'count': 1}",
                                                 "{'collection_year': 2013, 'count': 1}"], ordered=False)

    def test_event_per_month(self):
        """
        Ensure that the number of event per month is correctly aggregated.
        """
        self.assertQuerysetEqual(
            self.context.get('event_per_month'), ["{'collection_month': 3, 'count': 2}"], ordered=False)

    def test_sample_count(self):
        """
        Ensure the number of SampleMetadata per ProjectMetadata is counted correctly.
        """
        self.assertEqual(self.context.get('sample_count'), 1)

    def test_sample_geo_loc_name(self):
        """
        Ensure the number of SampleMetadata record per geo_loc_name is correctly aggregated.
        """
        self.assertQuerysetEqual(
            self.context.get('sample_geo_loc_name'), ["{'geo_loc_name': 'Chile: Patagonia', 'count': 1}"],
            ordered=False)

    def test_sample_env_biome(self):
        """
        Ensure the number of SampleMetadata record per env_biome is correctly aggregated.
        """
        self.assertQuerysetEqual(
            self.context.get('sample_env_biome'), ["{'env_biome': 'temperate forest', 'count': 1}"], ordered=False)

    def test_mof_count(self):
        """
        Ensure the number of Variable  record per ProjectMetadata is correctly counted.
        """
        self.assertEqual(self.context.get('mof_count'), 2)

    def test_mof_name(self):
        """
        Ensure the number of Variable record per name is correctly aggregated.
        """
        self.assertQuerysetEqual(self.context.get('mof_name'),
                                 ["{'name': 'has_next_generation_sequence_output_data', 'count': 1}",
                                  "{'name': 'org_carb', 'count': 1}"], ordered=False)

    def test_seq_count(self):
        """
        Ensure the number of Sequences per ProjectMetadata is correctly counted.
        """
        self.assertEqual(self.context.get('seq_count'), 2)

    def test_seq_target_gene(self):
        """
        Ensure the number of Sequences per target_gene is correctly aggregated
        """
        self.assertQuerysetEqual(
            self.context.get('seq_target_gene'), ["{'target_gene': '16S ssu rRNA', 'count': 2}"], ordered=False)

    def test_seq_target_subfg(self):
        """
        Ensure the number of Sequences per target_subfragment is correctly aggregated
        """
        self.assertQuerysetEqual(
            self.context.get('seq_target_subfg'), ["{'target_subfragment': 'v3-v5', 'count': 2}"], ordered=False)

    def test_seq_type(self):
        """
        Ensure the number of Sequences per type (study type) is correctly aggregated
        """
        self.assertQuerysetEqual(
            self.context.get('seq_type'), ["{'type': 'metagenomic', 'count': 2}"], ordered=False)

    def test_seq_run_type(self):
        """
        Ensure the number of Sequences per run_type is correctly aggregated
        """
        self.assertQuerysetEqual(
            self.context.get('seq_run_type'), ["{'run_type': 'single', 'count': 2}"], ordered=False)

    def test_seq_seqData_projectNumber(self):
        """
        Ensure the number of Sequences per seqData_projectNumber (BioProject number) is correctly aggregated
        """
        self.assertQuerysetEqual(
            self.context.get('seq_seqData_projectNumber'),
                             ["{'seqData_projectNumber': 'PRJNA239386', 'count': 1}",
                              "{'seqData_projectNumber': 'PRJNA239387', 'count': 1}"], ordered=False)
