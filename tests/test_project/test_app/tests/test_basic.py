from django.test import client, utils
from django.utils import simplejson as json, unittest

from test_project import test_runner
from test_project.test_app import documents

@utils.override_settings(DEBUG=True)
class BasicTest(test_runner.MongoEngineTestCase):
    apiUrl = '/api/v1/'
    c = client.Client()
    
    def makeUrl(self, link):
        return self.apiUrl + link + "/"
    
    def getUri(self, location):
        """
        Gets resource_uri from response location.
        """
        
        return self.apiUrl + location.split(self.apiUrl)[1]

    def test_basic(self):
        # Testing POST

        response = self.c.post(self.makeUrl('person'), '{"name": "Person 1"}', content_type='application/json')
        self.assertEqual(response.status_code, 201)

        person1_uri = response['location']

        response = self.c.get(person1_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['name'], 'Person 1')
        self.assertEqual(response['optional'], None)

        # Covered by Tastypie
        response = self.c.post(self.makeUrl('person'), '{"name": null}', content_type='application/json')
        self.assertContains(response, 'field has no data', status_code=400)

        # Covered by Tastypie
        response = self.c.post(self.makeUrl('person'), '{}', content_type='application/json')
        self.assertContains(response, 'field has no data', status_code=400)

        # Covered by MongoEngine validation
        response = self.c.post(self.makeUrl('person'), '{"name": []}', content_type='application/json')
        self.assertContains(response, 'only accepts string values', status_code=400)

        # Covered by MongoEngine validation
        response = self.c.post(self.makeUrl('person'), '{"name": {}}', content_type='application/json')
        self.assertContains(response, 'only accepts string values', status_code=400)
        
        response = self.c.post(self.makeUrl('person'), '{"name": "Person 2", "optional": "Optional"}', content_type='application/json')
        self.assertEqual(response.status_code, 201)

        person2_uri = response['location']

        response = self.c.get(person2_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['name'], 'Person 2')
        self.assertEqual(response['optional'], 'Optional')

        # Tastypie ignores additional field
        response = self.c.post(self.makeUrl('person'), '{"name": "Person 3", "additional": "Additional"}', content_type='application/json')
        self.assertEqual(response.status_code, 201)

        response = self.c.post(self.makeUrl('customer'), '{"person": "%s"}' % self.getUri(person1_uri), content_type='application/json')
        self.assertEqual(response.status_code, 201)

        customer_uri = response['location']

        response = self.c.get(customer_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['person']['name'], 'Person 1')
        self.assertEqual(response['person']['optional'], None)
        
        response = self.c.post(self.makeUrl('embededdocumentfieldtest'), '{"customer": {"name": "Embeded person 1"}}', content_type='application/json')
        self.assertEqual(response.status_code, 201)

        embededdocumentfieldtest_uri = response['location']

        response = self.c.get(embededdocumentfieldtest_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['customer']['name'], 'Embeded person 1')

        # Covered by MongoEngine validation
        response = self.c.post(self.makeUrl('dictfieldtest'), '{"dictionary": {}}', content_type='application/json')
        self.assertContains(response, 'required and cannot be empty', status_code=400)

        # Covered by Tastypie
        response = self.c.post(self.makeUrl('dictfieldtest'), '{"dictionary": null}', content_type='application/json')
        self.assertContains(response, 'field has no data', status_code=400)

        # Covered by MongoEngine validation
        response = self.c.post(self.makeUrl('dictfieldtest'), '{"dictionary": false}', content_type='application/json')
        self.assertContains(response, 'dictionaries may be used', status_code=400)
        
        response = self.c.post(self.makeUrl('dictfieldtest'), '{"dictionary": {"a": "abc", "number": 34}}', content_type='application/json')
        self.assertEqual(response.status_code, 201)

        dictfieldtest_uri = response['location']

        response = self.c.get(dictfieldtest_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['dictionary']['a'], 'abc')
        self.assertEqual(response['dictionary']['number'], 34)
        
        response = self.c.post(self.makeUrl('listfieldtest'), '{"intlist": [1, 2, 3, 4], "stringlist": ["a", "b", "c"]}', content_type='application/json')
        self.assertEqual(response.status_code, 201)

        listfieldtest_uri = response['location']

        response = self.c.get(listfieldtest_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['intlist'], [1, 2, 3, 4])
        self.assertEqual(response['stringlist'], ['a', 'b', 'c'])

        response = self.c.post(self.makeUrl('embeddedlistfieldtest'), '{"embeddedlist": [{"name": "Embeded person 1"}, {"name": "Embeded person 2"}]}', content_type='application/json')
        self.assertEqual(response.status_code, 201)

        embeddedlistfieldtest_uri = response['location']

        response = self.c.get(embeddedlistfieldtest_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['embeddedlist'][0]['name'], 'Embeded person 1')
        self.assertEqual(response['embeddedlist'][1]['name'], 'Embeded person 2')

        # Testing PUT

        response = self.c.put(person1_uri, '{"name": "Person 1z"}', content_type='application/json')
        self.assertEqual(response.status_code, 204)

        # Covered by Tastypie
        response = self.c.put(person1_uri, '{"name": null}', content_type='application/json')
        self.assertContains(response, 'field has no data', status_code=400)

        # Covered by Tastypie
        response = self.c.put(person1_uri, '{}', content_type='application/json')
        self.assertContains(response, 'field has no data', status_code=400)

        # Covered by MongoEngine validation
        response = self.c.put(person1_uri, '{"name": []}', content_type='application/json')
        self.assertContains(response, 'only accepts string values', status_code=400)

        # Covered by MongoEngine validation
        response = self.c.put(person1_uri, '{"name": {}}', content_type='application/json')
        self.assertContains(response, 'only accepts string values', status_code=400)

        response = self.c.get(person1_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['name'], 'Person 1z')

        response = self.c.put(customer_uri, '{"person": "%s"}' % self.getUri(person2_uri), content_type='application/json')
        self.assertEqual(response.status_code, 204)

        response = self.c.get(customer_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['person']['name'], 'Person 2')
        self.assertEqual(response['person']['optional'], 'Optional')

        response = self.c.put(embededdocumentfieldtest_uri, '{"customer": {"name": "Embeded person 1a"}}', content_type='application/json')
        self.assertEqual(response.status_code, 204)

        response = self.c.get(embededdocumentfieldtest_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['customer']['name'], 'Embeded person 1a')

        response = self.c.put(dictfieldtest_uri, '{"dictionary": {"a": 341, "number": "abcd"}}', content_type='application/json')
        self.assertEqual(response.status_code, 204)

        response = self.c.get(dictfieldtest_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['dictionary']['number'], 'abcd')
        self.assertEqual(response['dictionary']['a'], 341)

        response = self.c.put(listfieldtest_uri, '{"intlist": [1, 2, 4], "stringlist": ["a", "b", "c", "d"]}', content_type='application/json')
        self.assertEqual(response.status_code, 204)

        response = self.c.get(listfieldtest_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['intlist'], [1, 2, 4])
        self.assertEqual(response['stringlist'], ['a', 'b', 'c', 'd'])

        response = self.c.put(embeddedlistfieldtest_uri, '{"embeddedlist": [{"name": "Embeded person 1a"}, {"name": "Embeded person 2a"}]}', content_type='application/json')
        self.assertEqual(response.status_code, 204)

        response = self.c.get(embeddedlistfieldtest_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['embeddedlist'][0]['name'], 'Embeded person 1a')
        self.assertEqual(response['embeddedlist'][1]['name'], 'Embeded person 2a')

        # TODO: Test patch

        response = self.c.delete(person1_uri)
        self.assertEqual(response.status_code, 204)

        response = self.c.get(person1_uri)
        self.assertEqual(response.status_code, 404)

    def test_polymorphic(self):
        response = self.c.post(self.makeUrl('person'), '{"name": "Person 1"}', content_type='application/json; type=person')
        self.assertEqual(response.status_code, 201)

        # Tastypie ignores additional field
        response = self.c.post(self.makeUrl('person'), '{"name": "Person 1z", "strange": "Foobar"}', content_type='application/json; type=person')
        self.assertEqual(response.status_code, 201)

        response = self.c.post(self.makeUrl('person'), '{"name": "Person 2", "strange": "Foobar"}', content_type='application/json; type=strangeperson')
        self.assertEqual(response.status_code, 201)

        # Field "name" is required
        response = self.c.post(self.makeUrl('person'), '{"strange": "Foobar"}', content_type='application/json; type=strangeperson')
        self.assertContains(response, 'field has no data', status_code=400)

        # Field "strange" is required
        response = self.c.post(self.makeUrl('person'), '{"name": "Person 2"}', content_type='application/json; type=strangeperson')
        self.assertContains(response, 'field has no data', status_code=400)

        response = self.c.get(self.makeUrl('person'))
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(len(response['objects']), 3)
        self.assertEqual(response['objects'][0]['name'], 'Person 1')
        self.assertEqual(response['objects'][0]['resource_type'], 'person')
        self.assertEqual(response['objects'][1]['name'], 'Person 1z')
        self.assertEqual(response['objects'][1]['resource_type'], 'person')
        self.assertEqual(response['objects'][2]['name'], 'Person 2')
        self.assertEqual(response['objects'][2]['strange'], 'Foobar')
        self.assertEqual(response['objects'][2]['resource_type'], 'strangeperson')

        person1_uri = response['objects'][0]['resource_uri']
        person2_uri = response['objects'][2]['resource_uri']

        response = self.c.put(person1_uri, '{"name": "Person 1a"}', content_type='application/json; type=person')
        self.assertEqual(response.status_code, 204)

        response = self.c.get(person1_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['name'], 'Person 1a')

        # Changing existing resource type (type->subtype)

        # Field "name" is required
        response = self.c.put(person1_uri, '{"strange": "something"}', content_type='application/json; type=strangeperson')
        self.assertContains(response, 'field has no data', status_code=400)

        # Field "strange" is required
        response = self.c.put(person1_uri, '{"name": "Person 1a"}', content_type='application/json; type=strangeperson')
        self.assertContains(response, 'field has no data', status_code=400)

        response = self.c.put(person1_uri, '{"name": "Person 1a", "strange": "something"}', content_type='application/json; type=strangeperson')
        # Object got replaced, so we get 201 with location, but we do not want a
        # new object, so redirect should match initial resource URL
        self.assertRedirects(response, person1_uri, status_code=201)

        response = self.c.get(person1_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['name'], 'Person 1a')
        self.assertEqual(response['strange'], 'something')
        self.assertEqual(response['resource_type'], 'strangeperson')

        response = self.c.put(person2_uri, '{"name": "Person 2a", "strange": "FoobarXXX"}', content_type='application/json; type=strangeperson')
        self.assertEqual(response.status_code, 204)

        response = self.c.get(person2_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['name'], 'Person 2a')
        self.assertEqual(response['strange'], 'FoobarXXX')

        # Changing resource type again (subtype->type)
        response = self.c.put(person1_uri, '{"name": "Person 1c"}', content_type='application/json; type=person')
        self.assertRedirects(response, person1_uri, status_code=201)

        response = self.c.get(person1_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['name'], 'Person 1c')
        self.assertEqual(response['resource_type'], 'person')

        response = self.c.put(person2_uri, '{"name": "Person 2c", "strange": "something"}', content_type='application/json; type=person')
        # Additional fields are ignored
        self.assertRedirects(response, person2_uri, status_code=201)

        response = self.c.get(person2_uri)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)

        self.assertEqual(response['name'], 'Person 2c')
        self.assertEqual(response['resource_type'], 'person')

        # TODO: Test patch requests (https://code.djangoproject.com/ticket/17797)
        # TODO: Test delete