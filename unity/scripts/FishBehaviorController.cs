using System.Collections;
using UnityEngine;

namespace SeaPhotography.Ecology
{
    [RequireComponent(typeof(Animator))]
    public class FishBehaviorController : MonoBehaviour
    {
        [Header("Categorization")]
        public string speciesId = "shark";
        public string lifeStage = "mature_male";

        [Header("Movement Metrics")]
        public float swimSpeed = 3.0f;
        public float turnSpeed = 2.0f;
        public float swimWiggleAmplitude = 0.5f;
        public float aquaticDepthLimit = -40f;

        [Header("State Machines")]
        public bool isTased = false;
        public bool isCaught = false;
        public bool hasBeenPhotographed = false;

        private Animator anim;
        private Vector3 targetWanderPoint;
        private float wanderTimer = 0f;

        void Start()
        {
            anim = GetComponent<Animator>();
            PickNewWanderTarget();
            
            // Adjust local scale based on development stages
            if (lifeStage == "fry")
                transform.localScale = Vector3.one * 0.15f;
            else if (lifeStage == "juvenile")
                transform.localScale = Vector3.one * 0.45f;
            else if (lifeStage == "mature_female")
                transform.localScale = Vector3.one * 1.1f;
            else
                transform.localScale = Vector3.one * 1.0f; // mature_male
        }

        void Update()
        {
            if (isTased)
            {
                ApplyTasedFallDown();
                return;
            }

            if (isCaught)
            {
                ApplyCaughtQuiver();
                return;
            }

            WanderSwim();
        }

        private void WanderSwim()
        {
            wanderTimer += Time.deltaTime;
            if (wanderTimer > 8f || Vector3.Distance(transform.position, targetWanderPoint) < 3f)
            {
                PickNewWanderTarget();
            }

            // Smooth rotation towards target
            Vector3 targetDir = targetWanderPoint - transform.position;
            if (targetDir != Vector3.zero)
            {
                Quaternion targetRot = Quaternion.LookRotation(targetDir);
                transform.rotation = Quaternion.Slerp(transform.rotation, targetRot, Time.deltaTime * turnSpeed);
            }

            // Swim forward along custom spline curve
            transform.Translate(Vector3.forward * (swimSpeed * Time.deltaTime));

            // Set Animator speeds to match wiggling amplitude in rigs
            if (anim != null)
            {
                anim.SetFloat("SwimSpeedMultiplier", swimSpeed * 0.8f);
            }
        }

        private void PickNewWanderTarget()
        {
            wanderTimer = 0f;
            Vector3 randomOffset = Random.insideUnitSphere * 20f;
            randomOffset.y = Mathf.Clamp(randomOffset.y, aquaticDepthLimit, -1.0f);
            targetWanderPoint = transform.position + randomOffset;
        }

        #region PLAYER INTERACTION DISPATCHERS

        /// <summary>
        /// Triggered when the stun taser gun impacts the fish's outer epidermal layers.
        /// </summary>
        public void ApplyStunImpact()
        {
            if (isTased) return;
            isTased = true;
            Debug.Log($"[TASER_GUN] Stunned species: {speciesId} at age profile: {lifeStage}!");

            if (anim != null)
            {
                // Trigger standard skeletal spastic action baked in the package
                anim.Play("Action_Spasm_Sink");
            }

            StartCoroutine(RecoverFromStunRoutine());
        }

        private IEnumerator RecoverFromStunRoutine()
        {
            yield return new WaitForSeconds(6.0f); // 6 seconds temporary paralysis
            isTased = false;
            PickNewWanderTarget();
            if (anim != null)
            {
                anim.Play("Swim_Idle");
            }
        }

        private void ApplyTasedFallDown()
        {
            // Sinks dead weights slowly to simulate taser knockout
            transform.Translate(Vector3.down * (0.4f * Time.deltaTime), Space.World);
            // Rotates slightly belly-up
            transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.Euler(180, transform.rotation.eulerAngles.y, 0), Time.deltaTime * 0.5f);
        }

        /// <summary>
        /// Triggered when caught by marine biologist sample net.
        /// </summary>
        public void ApplyNetCapture()
        {
            if (isCaught) return;
            isCaught = true;
            if (anim != null)
            {
                anim.Play("Action_Net_Flap");
            }
        }

        private void ApplyCaughtQuiver()
        {
            // Lock movement but flutter erratic position
            transform.position += Random.insideUnitSphere * 0.05f;
        }

        /// <summary>
        /// Triggered when intense light source is directed towards the fish's specialized pupil centers.
        /// </summary>
        public void ApplyHighIntensityLight(Vector3 lightSourcePosition)
        {
            // Reposition wander point away from light
            Vector3 scatterDirection = (transform.position - lightSourcePosition).normalized;
            targetWanderPoint = transform.position + scatterDirection * 15f;
            targetWanderPoint.y = Mathf.Clamp(targetWanderPoint.y, aquaticDepthLimit, -1.0f);
            
            if (anim != null)
            {
                anim.Play("Action_Dazzled_Turn");
            }

            // Accelerate speed temporarily to perform rapid escape
            StartCoroutine(SpeedBurstRoutine());
        }

        private IEnumerator SpeedBurstRoutine()
        {
            float normalSpeed = swimSpeed;
            swimSpeed *= 2.5f;
            yield return new WaitForSeconds(3.5f);
            swimSpeed = normalSpeed;
        }

        #endregion

        #region PROCEDURAL PHOTOGRAPHY SYSTEM

        /// <summary>
        /// Analyzes the quality of a photograph taken of this specific fish instance.
        /// Returns a scientific grade letter (A, B, C, F) and a catalog composition value.
        /// </summary>
        public PhotoResult CapturePhotograph(Camera camera, LayerMask obstacleLayers)
        {
            PhotoResult result = new PhotoResult();
            result.species = speciesId;
            result.stage = lifeStage;

            // 1. Calculate Visibility / Framing
            Vector3 viewportPos = camera.WorldToViewportPoint(transform.position);
            bool inFrame = viewportPos.x >= 0.1f && viewportPos.x <= 0.9f &&
                           viewportPos.y >= 0.1f && viewportPos.y <= 0.9f &&
                           viewportPos.z > 0;

            if (!inFrame)
            {
                result.compositionScore = 0f;
                result.photoGrade = "F (Out of Frame)";
                return result;
            }

            // 2. Line of Sight Raycast Obstruction check (reefs, kelps, cages block photography)
            Vector3 rayDirection = transform.position - camera.transform.position;
            float distance = rayDirection.magnitude;
            RaycastHit hit;

            if (Physics.Raycast(camera.transform.position, rayDirection.normalized, out hit, distance, obstacleLayers))
            {
                result.compositionScore = 15f; // Partially obscured
                result.photoGrade = "D (Obstructed)";
                return result;
            }

            // 3. Orientation Score (Side-profile and front profile photograph captures are more scientific!)
            float facingDot = Vector3.Dot(transform.right, -camera.transform.forward); // perfect side profile dot
            float sidePhotoFactor = Mathf.Abs(facingDot); // 1.0 means perfect lateral profiling

            // 4. Distance sizing score (too far away vs perfectly focused close-up)
            float optimalDistance = transform.localScale.x * 6f; // Whales need larger distances than cichlids!
            float distanceScore = 1.0f - Mathf.Clamp01(Mathf.Abs(distance - optimalDistance) / (optimalDistance * 3f));

            // Compile composition quality percentage
            float qualityRaw = (sidePhotoFactor * 0.4f) + (distanceScore * 0.6f);
            result.compositionScore = Mathf.Round(qualityRaw * 100f);

            // Grade assignment
            if (result.compositionScore >= 85f) result.photoGrade = "A+ (Stunning Masterpiece)";
            else if (result.compositionScore >= 70f) result.photoGrade = "A (Excellent Research Photo)";
            else if (result.compositionScore >= 50f) result.photoGrade = "B (Good Document)";
            else result.photoGrade = "C (Blurry / Distance Snapshot)";

            hasBeenPhotographed = true;
            
            // Trigger dynamic photographic reaction
            if (anim != null)
            {
                anim.Play("Action_Flinch");
            }

            return result;
        }

        #endregion
    }

    public struct PhotoResult
    {
        public string species;
        public string stage;
        public float compositionScore;
        public string photoGrade;
    }
}
