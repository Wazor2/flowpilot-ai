import { Customer } from '../models';
import { mockCustomers } from '../demoData';

export class CustomerRepository {
  private customers: Customer[] = [...mockCustomers];

  async getById(id: string): Promise<Customer | undefined> {
    return Promise.resolve(this.customers.find(c => c.id === id));
  }

  async getAlternateContact(customerId: string): Promise<string | null> {
    // Simulated alternate contact discovery for demo
    if (customerId === "CUST-003") {
      return Promise.resolve("accounts@abc.com");
    }
    return Promise.resolve(null);
  }
}
