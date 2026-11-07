import api from './axios'
import type { ApiSuccess, SetupStatus, SetupPayload, SetupResult } from '../types'
import type { AxiosResponse } from 'axios'

export async function getSetupStatus(): Promise<AxiosResponse<ApiSuccess<SetupStatus>>> {
  return api.get('/api/setup/status')
}

export async function performSetup(data: SetupPayload): Promise<AxiosResponse<ApiSuccess<SetupResult>>> {
  return api.post('/api/setup', data)
}

