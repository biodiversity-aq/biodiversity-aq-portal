import datetime

from django.core.cache import cache
from django.urls import reverse
from django.test import TestCase

from polaaar.models import ProjectMetadata


class ProjectMetadataDetailTest(TestCase):
    """Ensure ProjectMetadataDetailView returns correct information."""
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

    def test_context_event_count(self):
        """
        Ensure that the event_count has the correct value.
        """
        self.assertEqual(self.context.get('event_count'), 2)

    def test_context_event_per_year(self):
        """
        Ensure that the event per year is correctly aggregated
        """
        self.assertQuerysetEqual(
            self.context.get('event_per_year'), ["{'collection_year': 2012, 'count': 1}",
                                                 "{'collection_year': 2013, 'count': 1}"], ordered=False)

    def test_context_event_per_month(self):
        """
        Ensure that the number of event per month is correctly aggregated.
        """
        self.assertQuerysetEqual(
            self.context.get('event_per_month'), ["{'collection_month': 3, 'count': 2}"], ordered=False)

    def test_context_sample_count(self):
        """
        Ensure the number of SampleMetadata per ProjectMetadata is counted correctly.
        """
        self.assertEqual(self.context.get('sample_count'), 1)

    def test_context_sample_geo_loc_name(self):
        """
        Ensure the number of SampleMetadata record per geo_loc_name is correctly aggregated.
        """
        self.assertQuerysetEqual(
            self.context.get('sample_geo_loc_name'), ["{'geo_loc_name': 'Chile: Patagonia', 'count': 1}"],
            ordered=False)

    def test_context_sample_env_biome(self):
        """
        Ensure the number of SampleMetadata record per env_biome is correctly aggregated.
        """
        self.assertQuerysetEqual(
            self.context.get('sample_env_biome'), ["{'env_biome': 'temperate forest', 'count': 1}"], ordered=False)

    def test_context_mof_count(self):
        """
        Ensure the number of Variable  record per ProjectMetadata is correctly counted.
        """
        self.assertEqual(self.context.get('mof_count'), 2)

    def test_context_mof_name(self):
        """
        Ensure the number of Variable record per name is correctly aggregated.
        """
        self.assertQuerysetEqual(self.context.get('mof_name'),
                                 ["{'name': 'has_next_generation_sequence_output_data', 'count': 1}",
                                  "{'name': 'org_carb', 'count': 1}"], ordered=False)

    def test_context_seq_count(self):
        """
        Ensure the number of Sequences per ProjectMetadata is correctly counted.
        """
        self.assertEqual(self.context.get('seq_count'), 2)

    def test_context_seq_target_gene(self):
        """
        Ensure the number of Sequences per target_gene is correctly aggregated
        """
        self.assertQuerysetEqual(
            self.context.get('seq_target_gene'), ["{'target_gene': '16S ssu rRNA', 'count': 2}"], ordered=False)

    def test_context_seq_target_subfg(self):
        """
        Ensure the number of Sequences per target_subfragment is correctly aggregated
        """
        self.assertQuerysetEqual(
            self.context.get('seq_target_subfg'), ["{'target_subfragment': 'v3-v5', 'count': 2}"], ordered=False)

    def test_context_seq_type(self):
        """
        Ensure the number of Sequences per type (study type) is correctly aggregated
        """
        self.assertQuerysetEqual(
            self.context.get('seq_type'), ["{'type': 'metagenomic', 'count': 2}"], ordered=False)

    def test_context_seq_run_type(self):
        """
        Ensure the number of Sequences per run_type is correctly aggregated
        """
        self.assertQuerysetEqual(
            self.context.get('seq_run_type'), ["{'run_type': 'single', 'count': 2}"], ordered=False)

    def test_context_seq_seqData_projectNumber(self):
        """
        Ensure the number of Sequences per seqData_projectNumber (BioProject number) is correctly aggregated
        """
        self.assertQuerysetEqual(
            self.context.get('seq_seqData_projectNumber'),
            ["{'seqData_projectNumber': 'PRJNA239386', 'count': 1}",
             "{'seqData_projectNumber': 'PRJNA239387', 'count': 1}"], ordered=False)

    def test_context_license(self):
        """
        Ensure the license can be obtained through eml
        """
        self.assertEqual(self.context.get('license'), 'http://creativecommons.org/licenses/by/4.0/legalcode')

    def test_context_citation(self):
        """
        Ensure the citation obtained is formatted correctly
        """
        now = datetime.datetime.now().date()
        citation = "Barber D, Ehn J, Pucko M, Rysgaard S, Deming J, Bowman J, Papakyriakou T, Galley R, " \
                   "Sogaard D (2019): Microorganisms in frost flowers on young Arctic sea ice, comparison " \
                   "between different ice types. v1.0. SCAR - Microbial Antarctic Resource System. Dataset/Metadata. " \
                   "https://ipt.biodiversity.aq/resource?r=microorganisms_in_frost_flowers_on_young_arctic_sea_ice&v=1.0 " \
                   "(Available: Polar 'Omics Links to Antarctic, Arctic and Alpine Research. Antarctic Biodiversity " \
                   "Portal. Scientific Committee for Antarctic Research. www.biodiversity.aq/pola3r. Accessed: {})".format(
            now)
        self.assertEqual(self.context.get('citation'), '{}'.format(citation))

    def test_context_reference(self):
        """
        Ensure the reference is populated in context
        """
        self.assertQuerysetEqual(self.context.get('ref'), ['<Reference: my reference.>'])

    def test_geoserver_host_no_trailing_slash(self):
        """
        Ensure the geoserver host has no trailing slash
        """
        geoserver_host = self.context.get('geoserver_host')
        self.assertNotEqual(geoserver_host[-1:], '/')

    def test_cache_created(self):
        """
        Ensure context is cached after the first visit of the project
        """
        self.client.get(reverse('polaaar:project_metadata_detail', args=[1, ]))
        # cache should be created after the GET request
        project_cache = cache.get('project1_2020-08-20')
        self.assertTrue(project_cache)


class ProjectMetadataListTest(TestCase):
    fixtures = ['polaaar/project_metadata_list.json']
    maxDiff = None

    def test_search_results_does_not_return_private_project(self):
        """
        Ensure that search does not return private project
        """
        # only ProjectMetadata with is_public=False has the word "private" in project_name and abstract
        response = self.client.get(reverse('polaaar:project_metadata_list'), data={'q': 'private'})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, [])

    def test_search_returns_relevant_results_only(self):
        """
        Ensure that search only returns hits
        """
        response = self.client.get(reverse('polaaar:project_metadata_list'), data={'q': 'arctic'})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<ProjectMetadata: arctic project>'])

    def test_return_all_public_projects_without_search_term(self):
        """
        Ensure that all ProjectMetadata with is_public=True is returned if the search term is not provided
        """
        response = self.client.get(reverse('polaaar:project_metadata_list'), data={'q': ''})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<ProjectMetadata: arctic project>',
                                      '<ProjectMetadata: a public belgian antarctic dataset>'])

    def test_display_no_results_message(self):
        """
        Ensure that a message is returned if no result found.
        """
        response = self.client.get(reverse('polaaar:project_metadata_list'), data={'q': 'sadfjhaliusent'})
        self.assertContains(response, 'Sorry, no result.', status_code=200, html=True)


class ProjectMetadataListPaginationTest(TestCase):

    def setUp(self):
        ProjectMetadata.objects.create(project_name='antarctic project', abstract='antarctic abstract',
                                       created_on=datetime.datetime.now(), is_public=True)
        for i in range(1, 30):
            ProjectMetadata.objects.create(project_name='test project', abstract='test project abstract',
                                           created_on=datetime.datetime.now(), is_public=True)

    def test_no_previous_next_button_if_not_paginated(self):
        """
        Ensure that there is no previous/next page button if result is not paginated
        """
        response = self.client.get(reverse('polaaar:project_metadata_list'), data={'q': 'antarctic'})
        self.assertNotContains(response, 'Sorry, no result.', status_code=200, html=True)
        self.assertNotContains(response, 'Previous', status_code=200, html=True)  # fraction of previous button
        self.assertNotContains(response, 'Next', status_code=200, html=True)  # fraction of  next button

    def test_next_button_rendered(self):
        """
        Ensure that Next button is rendered when the results are paginated
        """
        response = self.client.get(reverse('polaaar:project_metadata_list'), data={'q': 'test'})  # returns 30 results
        self.assertNotContains(response, 'Sorry, no result.', status_code=200, html=True)
        self.assertContains(response, 'href="?q=test&page=2">Next</a>', status_code=200)  # fraction of next button
        self.assertNotContains(response, '>Previous</a>', status_code=200)  # fraction of previous button

    def test_previous_next_button_rendered(self):
        """
        Ensure that Previous and Next button are rendered when the results are paginated
        """
        response = self.client.get(reverse('polaaar:project_metadata_list'),
                                   data={'q': 'test', 'page': 2})  # returns 30 results
        self.assertNotContains(response, 'Sorry, no result.', status_code=200, html=True)
        self.assertContains(response, 'href="?q=test&page=3">Next</a>', status_code=200)  # fraction of next button
        self.assertContains(response, 'href="?q=test&page=1">Previous</a>',
                            status_code=200)  # fraction of previous button


class EnvironmentListTest(TestCase):
    """Ensure that Environment search renders correctly."""
    fixtures = ['polaaar/environment_list.json']
    maxDiff = None

    def test_search_results_do_not_return_private_data(self):
        """Ensure that search will not return Environment data associated with ProjectMetadata which has
        is_public=False."""
        response = self.client.get(reverse('polaaar:env_search'), data={'variable': 2, 'text': 'PRIVATE'})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, [])

    def test_search_text(self):
        """Ensure that text search for Environment instance with Variable var_type=TXT"""
        response = self.client.get(reverse('polaaar:env_search'), data={'variable': 2, 'text': 'PUBLIC'})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<Environment: gr_brine_pk_2>'])

    def test_search_numeric_min(self):
        """Ensure that min value search for Environment instance with Variable var_type=NUM"""
        response = self.client.get(reverse('polaaar:env_search'), data={'variable': 3, 'min_value': 12})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<Environment: gr_brine_concentration_12>',
                                      '<Environment: gr_brine_concentration_20>'], ordered=False)

    def test_search_numeric_max(self):
        """Ensure that max value search for Environment instance with Variable var_type=NUM"""
        response = self.client.get(reverse('polaaar:env_search'), data={'variable': 3, 'max_value': 12})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<Environment: gr_brine_concentration_12>'])

    def test_search_numeric_range(self):
        """Ensure that range search works for Environment instance with Variable var_type=NUM"""
        response = self.client.get(reverse('polaaar:env_search'), data={'variable': 3, 'min_value': 15,
                                                                        'max_value': 20})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<Environment: gr_brine_concentration_20>'])

    def test_search_numeric_text(self):
        """Search for text in numeric field should returns nothing"""
        response = self.client.get(reverse('polaaar:env_search'), data={'variable': 3, 'text': '12'})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, [])

    def test_search_results_geojson(self):
        """Ensure geojson of the event is returned"""
        # should return the geojson of event_id=1 (environment_id=4)
        response = self.client.get(reverse('polaaar:env_search'), data={'variable': 3, 'max_value': 12})
        event_geojson = response.context.get('event_geojson')
        expected_geojson = '{"type": "FeatureCollection", "crs": {"type": "name", "properties": {"name": "EPSG:4326"}}, "features": [{"type": "Feature", "properties": {"project_metadata": 1}, "geometry": {"type": "Point", "coordinates": [-20.311, 74.468]}}]}'
        self.assertEqual(event_geojson, expected_geojson)

    def test_return_all_public_data_without_query_param(self):
        """This should represents the environment search page before search was performed."""
        response = self.client.get(reverse('polaaar:env_search'))
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<Environment: gr_brine_concentration_12>',
                                      '<Environment: gr_brine_concentration_20>',
                                      '<Environment: gr_brine>', '<Environment: gr_brine_pk_2>'])

    def test_display_no_results_message(self):
        """Ensure that a message is displayed when there is no search result"""
        response = self.client.get(reverse('polaaar:env_search'), data={'variable': 3, 'text': '12'})
        self.assertContains(response, 'Sorry, no result.', status_code=200, html=True)


class SequenceListTest(TestCase):
    fixtures = ['polaaar/sequence_list.json']
    maxDiff = None

    def test_search_results_does_not_return_private_data(self):
        """Ensure Sequences associated with ProjectMetadata is_public=False is not returned"""
        response = self.client.get(reverse('polaaar:seq_search'), data={'q': 'private'})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, [])

    def test_search_mid(self):
        """Ensure MID field is searchable"""
        response = self.client.get(reverse('polaaar:seq_search'), data={'q': 'my public mid'})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<Sequences: my public sequence>'])

    def test_search_target_gene(self):
        """Ensure target_gene field is searchable"""
        response = self.client.get(reverse('polaaar:seq_search'), data={'q': '16S ssu rRNA'})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<Sequences: my public sequence>'])

    def test_search_target_subfragment(self):
        """Ensure target_subfragment field is searchable"""
        response = self.client.get(reverse('polaaar:seq_search'), data={'q': 'v3-v5'})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<Sequences: my public sequence>'])

    def test_search_type(self):
        """Ensure type field is searchable"""
        response = self.client.get(reverse('polaaar:seq_search'), data={'q': 'metagenomic'})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<Sequences: my public sequence>'])

    def test_search_primerName_forward(self):
        """Ensure primerName_forward field is searchable"""
        response = self.client.get(reverse('polaaar:seq_search'), data={'q': '357F'})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<Sequences: my public sequence>'])

    def test_search_primerName_reverse(self):
        """Ensure primerName_reverse field is searchable"""
        response = self.client.get(reverse('polaaar:seq_search'), data={'q': '926R'})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<Sequences: my public sequence>'])

    def test_search_run_type(self):
        """Ensure run_type field is searchable"""
        response = self.client.get(reverse('polaaar:seq_search'), data={'q': 'single'})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<Sequences: my public sequence>'])

    def test_search_project_metadata_abstract(self):
        """Ensure target_subfragment field is searchable"""
        response = self.client.get(reverse('polaaar:seq_search'), data={'q': 'Amplicon sequencing dataset (454 pyrosequencing)'})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<Sequences: my public sequence>', '<Sequences: my public sequence 2>'],
                                 ordered=False)

    def test_search_project_metadata_project_name(self):
        """Ensure target_subfragment field is searchable"""
        response = self.client.get(reverse('polaaar:seq_search'), data={'q': 'frost flowers on young Arctic sea ice'})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<Sequences: my public sequence>',
                                      '<Sequences: my public sequence 2>'], ordered=False)

    def test_return_all_public_projects_without_search_term(self):
        """Ensure that all Sequence associated with ProjectMetadata which has is_public=True is returned if the
        search term is not provided"""
        response = self.client.get(reverse('polaaar:seq_search'), data={'q': ''})
        qs = response.context.get('object_list')
        self.assertQuerysetEqual(qs, ['<Sequences: my public sequence>',
                                      '<Sequences: my public sequence 2>'], ordered=False)

    def test_display_no_results_message(self):
        """Ensure that a message is returned if no result found."""
        response = self.client.get(reverse('polaaar:seq_search'), data={'q': 'sadfjhaliusent'})
        self.assertContains(response, 'Sorry, no result.', status_code=200, html=True)
