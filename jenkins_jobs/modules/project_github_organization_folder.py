
"""
github organization folder

Job with inline script example:

.. literalinclude::
   /../../tests/yamlparser/fixtures/project_github_organization_folder_template001.yml

"""
import logging
import xml.etree.ElementTree as XML
import jenkins_jobs.modules.base

from jenkins_jobs.modules import helpers

logger = logging.getLogger(str(__name__))


class GithubOrganizationFolder(jenkins_jobs.modules.base.Base):
    sequence = 0

    def root_xml(self, data):
        xml_parent = XML.Element(
            ('jenkins.'
             'branch.OrganizationFolder'))
        xml_parent.attrib['plugin'] = 'branch-api'

        if 'github-organization-folder' not in data:
            return xml_parent

        project_def = data['github-organization-folder']

        properties = XML.SubElement(xml_parent, 'properties')
        folder_config = XML.SubElement(
            properties,
            'org.jenkinsci.plugins.pipeline.modeldefinition.config.FolderConfig')
        folder_config.attrib['plugin'] = "pipeline-model-definition"
        XML.SubElement(folder_config, 'dockerLabel')
        registry = XML.SubElement(
            folder_config, 'registry')
        registry.attrib['plugin'] = "docker-commons"

        folder_credentials_provider = XML.SubElement(
            properties,
            'jenkins.branch.NoTriggerOrganizationFolderProperty')
        XML.SubElement(folder_credentials_provider, 'branches').text = '.*'

        folder_views = XML.SubElement(xml_parent, 'folderViews')
        owner = XML.SubElement(folder_views, 'owner')
        owner.attrib['reference'] = '../..'

        health_metrics = XML.SubElement(xml_parent, 'healthMetrics')
        health_metrics_plugin = XML.SubElement(
            health_metrics,
            ('com.cloudbees.hudson.plugins.'
             'folder.health.WorstChildHealthMetric'))
        health_metrics_plugin.attrib['plugin'] = 'cloudbees-folder'
        XML.SubElement(health_metrics_plugin, 'nonRecursive').text = "false"

        icon = XML.SubElement(xml_parent, 'icon')
        icon.attrib['class'] = ('jenkins.branch.MetadataActionFolderIcon')
        icon_owner = XML.SubElement(icon, 'owner')
        icon_owner.attrib['class'] = 'jenkins.branch.OrganizationFolder'
        icon_owner.attrib['reference'] = '../..'
        icon.attrib['plugin'] = 'cloudbees-folder'

        orphaned_item_strategy = XML.SubElement(
            xml_parent, 'orphanedItemStrategy')
        orphaned_item_strategy.attrib['class'] = (
            'com.cloudbees.hudson.plugins.folder.computed.'
            'DefaultOrphanedItemStrategy')
        orphaned_item_strategy.attrib['plugin'] = 'cloudbees-folder'

        orphaned_item_strategy_items = []
        if 'prune-dead-branches' in project_def:
            orphaned_item_strategy_items.append(
                ('prune-dead-branches', 'pruneDeadBranches',
                 False, [True, False]))

        orphaned_item_strategy_items.extend([
            ('days-to-keep', 'daysToKeep', -1),
            ('number-to-keep', 'numToKeep', -1),
        ])
        helpers.convert_mapping_to_xml(
            orphaned_item_strategy, project_def, orphaned_item_strategy_items)

        triggers = XML.SubElement(xml_parent, 'triggers')
        sub_trigger_items = []
        if 'timer-trigger' in project_def:
            timer_trigger = XML.SubElement(
                triggers, 'hudson.triggers.TimerTrigger')
            sub_trigger_items.append((timer_trigger, project_def,
                                      [('timer-trigger', 'spec', None)]))
        if 'periodic-folder-trigger' in project_def:
            periodic_folder_trigger = XML.SubElement(
                triggers,
                ('com.cloudbees.hudson.plugins.'
                 'folder.computed.PeriodicFolderTrigger'))
            periodic_folder_trigger.attrib['plugin'] = 'cloudbees-folder'
            sub_trigger_items.append(
                (periodic_folder_trigger, project_def,
                 [('periodic-folder-spec', 'spec', None),
                  ('periodic-folder-interval', 'interval', None)]))

        for parent, data, mapping in sub_trigger_items:
            helpers.convert_mapping_to_xml(parent, data, mapping)

        navigators = XML.SubElement(xml_parent, 'navigators')
        github_navigator = XML.SubElement(
            navigators,
            'org.jenkinsci.plugins.github__branch__source.GitHubSCMNavigator')
        github_navigator.attrib['plugin'] = 'github-branch-source'
        XML.SubElement(github_navigator, 'repoOwner').text = project_def['repo-owner']
        if 'repo-credentialsid' in project_def:
            XML.SubElement(github_navigator, 'credentialsId').text = project_def['repo-credentialsid']
        traits = XML.SubElement(github_navigator, 'traits')
        regex_scm_filter = XML.SubElement(traits, 'jenkins.scm.impl.trait.RegexSCMSourceFilterTrait')
        regex_scm_filter.attrib['plugin'] = "scm-api"
        XML.SubElement(regex_scm_filter, 'regex').text = project_def['regex-scm-filter']

        branch_discovery = XML.SubElement(traits,
            'org.jenkinsci.plugins.github__branch__source.BranchDiscoveryTrait')
        XML.SubElement(branch_discovery, 'strategyId').text = project_def['traits']['branch-discovery-strategy']

        pr_discovery = XML.SubElement(traits,
            'org.jenkinsci.plugins.github__branch__source.OriginPullRequestDiscoveryTrait')
        XML.SubElement(pr_discovery, 'strategyId').text = project_def['traits']['pr-discovery-strategy']

        fork_pr_discovery = XML.SubElement(traits,
            'org.jenkinsci.plugins.github__branch__source.ForkPullRequestDiscoveryTrait')
        XML.SubElement(fork_pr_discovery, 'strategyId').text = project_def['traits']['fork-pr-discovery-strategy']
        trust = XML.SubElement(fork_pr_discovery, 'trust')
        trust.attrib['class'] = 'org.jenkinsci.plugins.github_branch_source.ForkPullRequestDiscoveryTrait$TrustContributors'

        head_filer = XML.SubElement(traits,
            'jenkins.scm.impl.trait.WildcardSCMHeadFilterTrait')
        head_filer.attrib['plugin'] = "scm-api"
        XML.SubElement(head_filer, 'includes').text = project_def['traits']['includes']
        XML.SubElement(head_filer, 'excludes').text = project_def['traits']['excludes']

        factories = XML.SubElement(xml_parent, 'projectFactories')
        factory = XML.SubElement(
            factories,
            'org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProjectFactory')
        factory.attrib['plugin'] = "workflow-multibranch"
        XML.SubElement(factory, "scriptPath").text = project_def['jenkinsfile-path']
        XML.SubElement(xml_parent, 'buildStrategies')
        return xml_parent
