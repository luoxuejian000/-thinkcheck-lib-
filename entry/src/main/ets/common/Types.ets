export interface DiagnosisRequest {
  text: string
  domain: string
  weights: { lambda_u: number; lambda_d: number; lambda_a: number }
}