import { Communication, PolicyDocument } from '../models';
import { mockCommunications, mockPolicies } from '../demoData';

export class CommunicationRepository {
  private communications: Communication[] = [...mockCommunications];
  private policies: PolicyDocument[] = [...mockPolicies];

  async getHistoryByCustomerId(customerId: string): Promise<Communication[]> {
    return Promise.resolve(this.communications.filter(c => c.customer_id === customerId));
  }

  async getPolicies(): Promise<PolicyDocument[]> {
    return Promise.resolve(this.policies);
  }
}
