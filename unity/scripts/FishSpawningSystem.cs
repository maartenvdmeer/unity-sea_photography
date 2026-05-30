using System;
using System.Collections.Generic;
using UnityEngine;

namespace SeaPhotography.Ecology
{
    [System.Serializable]
    public class InteractionActions
    {
        public string tased;
        public string caught;
        public string light_observed;
        public string photographed;
    }

    [System.Serializable]
    public class LifeStageData
    {
        public string asset_model_name;
        public float length_meters;
        public float social_cohesion_factor;
        public float speed_scalar;
        public float reactivity_multiplier;
        public List<string> behaviors;
        public InteractionActions interactions;
    }

    [System.Serializable]
    public class SpeciesData
    {
        public string name;
        public string scientific_name;
        public string description;
        public string diet;
        public List<int> spawn_months;
        public List<string> spawn_locations;
        public Dictionary<string, LifeStageData> life_stages; // custom dictionary wrapper for Unity parsing
    }

    /// <summary>
    /// Spawns and manages the procedural fish population inside the active dive level
    /// based on seasonal calendars, diver locations, and age demographic profiles.
    /// </summary>
    public class FishSpawningSystem : MonoBehaviour
    {
        [Header("Ecology Settings")]
        [Range(1, 12)]
        public int currentMonth = 5; // Default to May
        public string currentDiveLocation = "Reef Wall";

        [Header("Spawn Configuration")]
        public float spawnRadius = 45f;
        public float spawnInterval = 3f;
        public int maxFishCount = 50;

        [Header("Prefabs Library")]
        [Tooltip("Assign models that map to the generated FBX names")]
        public List<GameObject> fishPrefabs; 

        private List<GameObject> activeFish = new List<GameObject>();
        private string metadataJson;
        private float spawnTimer = 0f;

        void Start()
        {
            LoadMetadataDatabase();
            SpawnInitialPopulation();
        }

        void Update()
        {
            spawnTimer += Time.deltaTime;
            if (spawnTimer >= spawnInterval)
            {
                spawnTimer = 0f;
                PruneDeadOrDistantFish();
                if (activeFish.Count < maxFishCount)
                {
                    TrySpawnProceduralFish();
                }
            }
        }

        private void LoadMetadataDatabase()
        {
            // Loads the generated fish_library_meta.json file from the resources folder
            TextAsset jsonAsset = Resources.Load<TextAsset>("fish_library_meta");
            if (jsonAsset != null)
            {
                metadataJson = jsonAsset.text;
                Debug.Log("Successfully loaded environmental procedural fish database!");
            }
            else
            {
                Debug.LogWarning("Procedural metadata file not found in Resources. Using offline defaults.");
            }
        }

        private void SpawnInitialPopulation()
        {
            int startingCount = maxFishCount / 2;
            for (int i = 0; i < startingCount; i++)
            {
                Vector3 spawnPos = transform.position + UnityEngine.Random.insideUnitSphere * (spawnRadius * 0.7f);
                spawnPos.y = Mathf.Clamp(spawnPos.y, -30f, -2f); // Restrict to secure diving depths
                SpawnFishAt(spawnPos);
            }
        }

        private void TrySpawnProceduralFish()
        {
            // Pick random locations around player
            Vector3 spawnPos = Camera.main.transform.position + UnityEngine.Random.onUnitSphere * spawnRadius;
            spawnPos.y = Mathf.Clamp(spawnPos.y, -30f, -2f);
            SpawnFishAt(spawnPos);
        }

        private void SpawnFishAt(Vector3 position)
        {
            if (fishPrefabs == null || fishPrefabs.Count == 0) return;

            // Pick a random prefab from the procedural library
            GameObject skeletonPrefab = fishPrefabs[UnityEngine.Random.Range(0, fishPrefabs.Count)];
            GameObject fishInstance = Instantiate(skeletonPrefab, position, UnityEngine.Random.rotation);

            // Dynamically assign behavior intelligence and bind metrics from the pipeline
            FishBehaviorController controller = fishInstance.AddComponent<FishBehaviorController>();
            
            // Map the parsed variables to the controller component
            ConfigureControllerByMetadata(controller, skeletonPrefab.name);

            activeFish.Add(fishInstance);
        }

        private void ConfigureControllerByMetadata(FishBehaviorController controller, string assetName)
        {
            // Example configuration: Fish_Shark_Mature_female -> Species: shark, Stage: mature_female
            string[] parts = assetName.Split('_');
            if (parts.Length >= 3)
            {
                controller.speciesId = parts[1].ToLower();
                controller.lifeStage = parts[2].ToLower();
            }
            else
            {
                controller.speciesId = "generic";
                controller.lifeStage = "mature_male";
            }

            // Set up fallback movement metrics
            controller.swimSpeed = 2.5f;
            controller.turnSpeed = 1.5f;
            controller.aquaticDepthLimit = -35f;
        }

        private void PruneDeadOrDistantFish()
        {
            Transform playerTrans = Camera.main.transform;
            activeFish.RemoveAll(fish => {
                if (fish == null) return true;

                float distance = Vector3.Distance(fish.transform.position, playerTrans.position);
                if (distance > spawnRadius * 1.5f)
                {
                    Destroy(fish);
                    return true;
                }
                return false;
            });
        }
    }
}
