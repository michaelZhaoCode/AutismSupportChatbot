import unittest
from app_functions import index, generate, retrieve_regions, storage_stats

class TestAppFunctions(unittest.TestCase):
    
    def test_index(self):
        """Test the index function returns the expected greeting."""
        result = index()
        self.assertEqual(result, "hello")
    
    def test_generate_valid(self):
        """Test the generate function with valid inputs."""
        response, status_code = generate(
            username="test_user",
            message="Hello, I need information about autism resources",
            usertype="adult"
        )
        self.assertEqual(status_code, 200)
        self.assertIn('response', response)
    
    def test_generate_invalid_usertype(self):
        """Test the generate function with invalid usertype."""
        response, status_code = generate(
            username="test_user",
            message="Hello",
            usertype="invalid_type"
        )
        self.assertEqual(status_code, 400)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'Invalid usertype')
    
    def test_generate_invalid_region_id(self):
        """Test the generate function with invalid region_id."""
        response, status_code = generate(
            username="test_user",
            message="Hello",
            usertype="adult",
            region_id="not_a_number"
        )
        self.assertEqual(status_code, 400)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'region_id must be an integer')
    
    def test_retrieve_regions(self):
        """Test the retrieve_regions function."""
        response, status_code = retrieve_regions()
        self.assertEqual(status_code, 200)
        self.assertIn('response', response)
    
    def test_storage_stats(self):
        """Test the storage_stats function."""
        response, status_code = storage_stats()
        self.assertEqual(status_code, 200)
        self.assertIn('response', response)


if __name__ == "__main__":
    # Simple manual testing
    print("Testing index function:", index())
    
    print("\nTesting generate function with valid inputs:")
    response, status = generate("test_user", "Hello, I need autism resources", "adult")
    print(f"Status: {status}, Response: {response}")
    
    print("\nTesting generate function with invalid usertype:")
    response, status = generate("test_user", "Hello", "invalid_type")
    print(f"Status: {status}, Response: {response}")
    
    print("\nTesting retrieve_regions function:")
    regions, status = retrieve_regions()
    print(f"Status: {status}, First few regions: {str(regions)[:200]}...")
    
    print("\nTesting storage_stats function:")
    stats, status = storage_stats()
    print(f"Status: {status}, Stats: {stats}")
    
    # Uncomment to run unit tests
    # unittest.main() 