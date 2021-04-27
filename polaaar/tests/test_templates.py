from datetime import datetime

from django.urls import reverse
from django.test import TestCase


class ProjectMetadataDetailTest(TestCase):
    """Ensure ProjectMetadataDetailView template renders correct information."""
    fixtures = ['polaaar/project_metadata_detail.json']
    maxDiff = None

    def setUp(self):
        project_metadata_detail_url = reverse('polaaar:project_metadata_detail', args=[1, ])
        self.response = self.client.get(project_metadata_detail_url)
        return self

    def test_project_name(self):
        """Ensure that project name is rendered"""
        self.assertContains(self.response,
                            'Microorganisms in frost flowers on young Arctic sea ice, comparison between different ice types')

    def test_download_source_button(self):
        """Ensure the download source csv button with the correct link is rendered"""
        get_project_file_url = reverse('polaaar:GetProjectFiles', args=(1,))
        download_source_button = '''href="{}">Download source csv</a>'''.format(get_project_file_url)
        self.assertContains(self.response, download_source_button)

    def test_download_polaaar_formatted_archive_button(self):
        """Ensure that the download project button is rendered"""
        export_project_url = reverse('polaaar:export_projects')
        self.assertContains(self.response, '{}?id=1'.format(export_project_url))

    def test_resource_url(self):
        """Ensure that resource url is rendered"""
        self.assertContains(self.response,
                            'https://ipt.biodiversity.aq/resource?r=microorganisms_in_frost_flowers_on_young_arctic_sea_ice&amp;v=1.0')

    def test_last_updated(self):
        last_updated = '''<th scope="row">Last updated</th>
                <td>Aug. 20, 2020</td>'''
        self.assertContains(self.response, last_updated)

    def test_abstract(self):
        """Ensure that abstract is rendered"""
        abstract = '''Amplicon sequencing dataset (454 pyrosequencing) of Bacteria in different types of young sea ice and sea ice brines in the Arctic ocean (North-East coast of Greenland)'''
        self.assertContains(self.response, abstract)

    def test_time_range(self):
        """Ensure that time range is rendered"""
        time_range = '''<th scope="row">Time range</th>
                    <td>Jan. 1, 2012 - Jan. 1, 2013</td>'''
        self.assertContains(self.response, time_range)

    def test_project_contact(self):
        """Ensure that project contact is rendered"""
        project_contact = '''<th scope="row">Project contact</th>
                <td>John Doe</td>'''
        self.assertContains(self.response, project_contact)

    def test_rights(self):
        """Ensure that the license is rendered"""
        license = '''<td><a href="http://creativecommons.org/licenses/by/4.0/legalcode">http://creativecommons.org/licenses/by/4.0/legalcode</a></td>'''
        self.assertContains(self.response, license)

    def test_sequence_data(self):
        """Ensure that Bioproject number is rendered"""
        self.assertContains(self.response, 'https://www.ncbi.nlm.nih.gov/bioproject/?term=PRJNA239386')

    def test_citation(self):
        """Ensure EML citation is rendered"""
        citation = '''Barber D, Ehn J, Pucko M, Rysgaard S, Deming J, Bowman J, Papakyriakou T, Galley R, Sogaard D (2019): Microorganisms in frost flowers on young Arctic sea ice, comparison between different ice types. v1.0. SCAR - Microbial Antarctic Resource System. Dataset/Metadata. <a href="https://ipt.biodiversity.aq/resource?r=microorganisms_in_frost_flowers_on_young_arctic_sea_ice&amp;v=1.0" rel="nofollow">https://ipt.biodiversity.aq/resource?r=microorganisms_in_frost_flowers_on_young_arctic_sea_ice&amp;v=1.0</a> (Available: Polar &#39;Omics Links to Antarctic, Arctic and Alpine Research. Antarctic Biodiversity Portal. Scientific Committee for Antarctic Research. <a href="http://www.biodiversity.aq/pola3r" rel="nofollow">www.biodiversity.aq/pola3r</a>. Accessed: {})'''.format(datetime.now().date())
        self.assertContains(self.response, citation)

    def test_sampling_event_count(self):
        """Ensure Event count is rendered"""
        event_records = '''<th scope="row">Sampling event records</th>
                                        <td>2</td>'''
        self.assertContains(self.response, event_records, html=True)

    def test_references(self):
        """Ensure Reference is rendered"""
        references = '''<th scope="row">References</th>
                            <td>
                                <ol>
                                    <li>my reference.</li>
                                </ol>
                            </td>'''
        self.assertContains(self.response, references, html=True)

    def test_sample_count(self):
        """Ensure SampleMetadata count is rendered"""
        sample_count = '''
            <th scope="row">Sample records</th>
            <td>1</td>'''
        self.assertContains(self.response, sample_count, html=True)

    def test_sequence_count(self):
        """Ensure Sequence count is rendered"""
        sequence_count = '''
        <th scope="row">Sequence metadata records</th>
        <td>2</td>        '''
        self.assertContains(self.response, sequence_count, html=True)

    def test_environment_count(self):
        """Ensure Variable count is rendered"""
        env_var_count = '''
        <th scope="row">Environmental metadata records</th>
        <td>2</td>
        '''
        self.assertContains(self.response, env_var_count, html=True)

    def test_collection_year_count(self):
        """Ensure Event collection_year and corresponding count is rendered"""
        year_count = '''
        <tr>
            <th>Year</th>
            <th>Records</th>
        </tr>
        <tr>
            <td>2012</td>
            <td>1</td>
        </tr>
        <tr>
            <td>2013</td>
            <td>1</td>
        </tr>'''
        self.assertContains(self.response, year_count, html=True)

    def test_collection_month_count(self):
        """Ensure Event collection_month and corresponding count is rendered"""
        month_count = '''
        <tr>
            <th>Month</th>
            <th>Records</th>
        </tr>
        <tr>
            <td>3</td>
            <td>2</td>
        </tr>'''
        self.assertContains(self.response, month_count, html=True)

    def test_geo_loc_name_count(self):
        """Ensure the SampleMetadata geo_loc_name is rendered"""
        geo_loc_name = '''<tr>
        <th scope="row">Location</th>
        <td>Chile: Patagonia</td>
        <td>1</td>
        </tr>
        '''
        self.assertContains(self.response, geo_loc_name, html=True)

    def test_env_biome_count(self):
        """Ensure the SampleMetadata env_biome and corresponding count is rendered"""
        env_biome = '''<tr>
        <th scope="row">Environmental biome</th>
        <td>temperate forest</td>
        <td>1</td>
        </tr>'''
        self.assertContains(self.response, env_biome, html=True)

    def test_target_gene_count(self):
        """Ensure the Sequences target_gene and corresponding count is rendered"""
        target_gene = '''<th scope="row">Target gene</th>
        <td>16S ssu rRNA</td>
        <td>2</td>
        '''
        self.assertContains(self.response, target_gene, html=True)

    def test_target_subfragment_count(self):
        """Ensure the Sequences target_subfragment and corresponding count is rendered"""
        target_subfragment = '''<tr>
        <th scope="row">Target subfragment</th>
        <td>v3-v5</td>
        <td>2</td>
        </tr>'''
        self.assertContains(self.response, target_subfragment, html=True)

    def test_sequence_type(self):
        """Ensure the Sequences type is rendered"""
        study_type = '''<tr>
        <th scope="row">Study type</th>
        <td>Metagenomic</td>
        <td>2</td>
        </tr>
        '''
        self.assertContains(self.response, study_type, html=True)

    def test_sequence_run_type(self):
        """Ensure the Sequences run_type is rendered"""
        run_type = '''<tr>
        <th scope="row">Run type</th>
        <td>single</td>
        <td>2</td>
        </tr>
        '''
        self.assertContains(self.response, run_type, html=True)

    def test_variable_count(self):
        """Ensure that each Variable and their corresponding count is rendered"""
        var_count = '''<tr>
        <th>Variable</th>
        <th>Records</th>
        </tr>
        <tr>
        <td>has_next_generation_sequence_output_data</td>
        <td>1</td>
        </tr>
        <tr>
        <td>org_carb</td>
        <td>1</td>
        </tr>
        '''
        self.assertContains(self.response, var_count, html=True)
